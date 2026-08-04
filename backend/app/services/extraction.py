from datetime import UTC, datetime
from pathlib import Path

import cv2
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.database.session import create_database_engine
from app.models.extraction import ExtractionJob, Frame
from app.models.video import Video
from app.schemas.extraction import ExtractionCreate
from app.services.frame import generate_thumbnail
from app.services.video import VideoService


def sampling_indices(frame_count: int, source_fps: float, mode: str, value: float) -> list[int]:
    if mode == "every_n_frames":
        step = int(value)
    elif mode == "frames_per_second":
        step = max(1, round(source_fps / value))
    else:
        step = max(1, round(source_fps * value))
    return list(range(0, frame_count, step))


class ExtractionService:
    def __init__(self, session: Session, storage_root: Path) -> None:
        self.session = session
        self.videos = VideoService(session, storage_root)

    def create(self, video_id: int, payload: ExtractionCreate) -> ExtractionJob:
        video = self.videos.get(video_id)
        existing = self.session.scalar(
            select(ExtractionJob).where(
                ExtractionJob.video_id == video_id, ExtractionJob.status.in_(["pending", "running"])
            )
        )
        if existing:
            raise AppError(
                "EXTRACTION_IN_PROGRESS", "An extraction is already running for this video.", 409
            )
        completed = self.session.scalar(
            select(ExtractionJob).where(
                ExtractionJob.video_id == video_id, ExtractionJob.status == "completed"
            )
        )
        if completed and not payload.overwrite:
            raise AppError(
                "EXTRACTION_EXISTS",
                "Frames already exist. Confirm overwrite to extract again.",
                409,
            )
        if payload.overwrite:
            self._remove_frames(video)
        total = len(
            sampling_indices(video.frame_count, video.fps, payload.mode, payload.mode_value)
        )
        job = ExtractionJob(
            project_id=video.project_id,
            video_id=video.id,
            total_frames=total,
            **payload.model_dump(exclude={"overwrite"}),
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get(self, job_id: int) -> ExtractionJob:
        job = self.session.get(ExtractionJob, job_id)
        if not job:
            raise AppError("EXTRACTION_JOB_NOT_FOUND", "The extraction job does not exist.", 404)
        return job

    def list(self, project_id: int) -> list[ExtractionJob]:
        return list(
            self.session.scalars(
                select(ExtractionJob)
                .where(ExtractionJob.project_id == project_id)
                .order_by(ExtractionJob.created_at.desc())
            )
        )

    def cancel(self, job_id: int) -> ExtractionJob:
        job = self.get(job_id)
        if job.status in {"pending", "running"}:
            job.status = "cancelling"
            self.session.commit()
            self.session.refresh(job)
        return job

    def _remove_frames(self, video: Video) -> None:
        frames = list(self.session.scalars(select(Frame).where(Frame.video_id == video.id)))
        root = Path(video.stored_path).parent.parent.resolve()
        for frame in frames:
            path = Path(frame.image_path).resolve()
            if path.is_relative_to(root):
                path.unlink(missing_ok=True)
        self.session.execute(delete(Frame).where(Frame.video_id == video.id))
        self.session.commit()


def run_extraction(job_id: int, database_url: str) -> None:
    engine = create_database_engine(database_url)
    with Session(engine) as session:
        job = session.get(ExtractionJob, job_id)
        if not job:
            return
        video = session.get(Video, job.video_id)
        if not video:
            job.status, job.error_message = "failed", "The source video record is missing."
            session.commit()
            return
        job.status, job.started_at = "running", datetime.now(UTC)
        session.commit()
        capture = cv2.VideoCapture(video.stored_path)
        output_dir = Path(video.stored_path).parent.parent / "frames" / str(video.id)
        output_dir.mkdir(parents=True, exist_ok=True)
        indices = sampling_indices(video.frame_count, video.fps, job.mode, job.mode_value)
        extension = ".jpg" if job.output_format == "jpeg" else ".png"
        try:
            for position, frame_number in enumerate(indices, 1):
                session.refresh(job)
                if job.status == "cancelling":
                    job.status, job.completed_at = "cancelled", datetime.now(UTC)
                    session.commit()
                    return
                capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ok, image = capture.read()
                if not ok:
                    raise ValueError(f"Could not decode frame {frame_number}.")
                height, width = image.shape[:2]
                if job.resize_width or job.resize_height:
                    scale = min(
                        (job.resize_width or width) / width, (job.resize_height or height) / height
                    )
                    width, height = max(1, round(width * scale)), max(1, round(height * scale))
                    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
                timestamp = frame_number / video.fps
                timestamp_ms = round(timestamp * 1000)
                filename = (
                    f"{Path(video.filename).stem}_frame_{frame_number:08d}"
                    f"_time_{timestamp_ms:010d}{extension}"
                )
                path = output_dir / filename
                params = [cv2.IMWRITE_JPEG_QUALITY, job.jpeg_quality] if extension == ".jpg" else []
                if not cv2.imwrite(str(path), image, params):
                    raise OSError(f"Could not write frame {frame_number}.")
                frame = Frame(
                    project_id=video.project_id,
                    video_id=video.id,
                    frame_number=frame_number,
                    timestamp_seconds=timestamp,
                    image_path=str(path),
                    width=width,
                    height=height,
                )
                session.add(frame)
                session.flush()
                thumbnail_path = (
                    output_dir.parent.parent / "thumbnails" / str(video.id) / f"{frame.id}.jpg"
                )
                generate_thumbnail(path, thumbnail_path)
                frame.thumbnail_path = str(thumbnail_path)
                job.processed_frames, job.progress = position, position / len(indices) * 100
                session.commit()
            job.status, job.progress, job.completed_at = "completed", 100, datetime.now(UTC)
            session.commit()
        except Exception as exc:
            job.status, job.error_message, job.completed_at = "failed", str(exc), datetime.now(UTC)
            session.commit()
        finally:
            capture.release()
            engine.dispose()
