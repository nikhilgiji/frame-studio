import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.database.session import create_database_engine
from app.models.export import ExportJob
from app.models.extraction import Frame
from app.models.project import Project
from app.models.review import FrameLabel, Label
from app.models.video import Video
from app.schemas.export import ExportCreate
from app.services.project import ProjectService


class ExportService:
    def __init__(self, session: Session, storage_root: Path) -> None:
        self.session = session
        self.storage_root = storage_root.resolve()

    def create(self, project_id: int, payload: ExportCreate) -> ExportJob:
        ProjectService(self.session, self.storage_root).get(project_id)
        export_root = (self.storage_root / "exports").resolve()
        destination = (export_root / payload.destination_name).resolve()
        if not destination.is_relative_to(export_root) or destination == export_root:
            raise AppError("UNSAFE_EXPORT_PATH", "The export destination is unsafe.", 409)
        job = ExportJob(
            project_id=project_id,
            destination_path=str(destination),
            export_mode=payload.export_mode,
            configuration_json=payload.model_dump_json(),
            status="pending",
            progress=0,
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get(self, job_id: int) -> ExportJob:
        job = self.session.get(ExportJob, job_id)
        if not job:
            raise AppError("EXPORT_JOB_NOT_FOUND", "The export job does not exist.", 404)
        return job

    def cancel(self, job_id: int) -> ExportJob:
        job = self.get(job_id)
        if job.status in {"pending", "running"}:
            job.status = "cancelling"
            self.session.commit()
            self.session.refresh(job)
        return job


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._") or "item"


def _destination(path: Path, policy: str) -> Path | None:
    if not path.exists() or policy == "overwrite":
        return path
    if policy == "skip":
        return None
    for index in range(1, 100000):
        candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise OSError("Could not resolve an export filename conflict.")


def run_export(job_id: int, database_url: str) -> None:
    engine = create_database_engine(database_url)
    with Session(engine) as session:
        job = session.get(ExportJob, job_id)
        if not job:
            return
        config = ExportCreate.model_validate_json(job.configuration_json)
        project = session.get(Project, job.project_id)
        job.status = "running"
        session.commit()
        try:
            statement = select(Frame).where(Frame.project_id == job.project_id)
            if config.export_mode == "selected":
                statement = statement.where(Frame.id.in_(config.frame_ids))
            elif config.export_mode == "favorites":
                statement = statement.where(Frame.favorite.is_(True))
            elif config.export_mode == "reviewed":
                statement = statement.where(Frame.review_status == "reviewed")
            elif config.export_mode == "label_folders" and config.label_ids:
                statement = statement.where(
                    Frame.id.in_(
                        select(FrameLabel.frame_id).where(FrameLabel.label_id.in_(config.label_ids))
                    )
                )
            frames = list(session.scalars(statement.order_by(Frame.id)))
            destination = Path(job.destination_path)
            destination.mkdir(parents=True, exist_ok=True)
            manifest_frames: list[dict[str, object]] = []
            for index, frame in enumerate(frames, 1):
                session.refresh(job)
                if job.status == "cancelling":
                    job.status = "cancelled"
                    job.completed_at = datetime.now(UTC)
                    session.commit()
                    return
                labels = list(
                    session.scalars(
                        select(Label)
                        .join(FrameLabel)
                        .where(FrameLabel.frame_id == frame.id)
                        .order_by(Label.position)
                    )
                )
                video = session.get(Video, frame.video_id)
                if not video:
                    raise ValueError(f"The source video for frame {frame.id} is missing.")
                source = Path(frame.image_path)
                base_name = (
                    _safe_name(f"{Path(video.filename).stem}_frame_{frame.frame_number:08d}")
                    + source.suffix.lower()
                )
                exported: list[str] = []
                if config.export_mode != "manifest":
                    folders = [destination / "images"]
                    if (
                        config.export_mode == "label_folders"
                        and config.multi_label_mode == "copy_each"
                    ):
                        folders = [
                            destination / _safe_name(label.name)
                            for label in labels
                            if not config.label_ids or label.id in config.label_ids
                        ]
                    for folder in folders:
                        folder.mkdir(parents=True, exist_ok=True)
                        target = _destination(folder / base_name, config.conflict)
                        if target:
                            shutil.copy2(source, target)
                            exported.append(str(target.relative_to(destination)))
                manifest_frames.append(
                    {
                        "source_video": video.filename,
                        "frame_number": frame.frame_number,
                        "timestamp_seconds": frame.timestamp_seconds,
                        "exported_filename": exported[0] if exported else None,
                        "exported_filenames": exported,
                        "labels": [label.name for label in labels],
                        "reviewed": frame.review_status == "reviewed",
                        "favorite": frame.favorite,
                        "rejected": frame.rejected,
                    }
                )
                job.progress = index / max(1, len(frames)) * 100
                session.commit()
            manifest = {
                "project": project.name if project else str(job.project_id),
                "frames": manifest_frames,
            }
            (destination / "manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
            job.status = "completed"
            job.progress = 100
            job.completed_at = datetime.now(UTC)
            session.commit()
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
            job.completed_at = datetime.now(UTC)
            session.commit()
        finally:
            engine.dispose()
