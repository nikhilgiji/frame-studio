import hashlib
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import cv2
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.video import Video
from app.repositories.video import VideoRepository
from app.schemas.video import ImportIssue, VideoImportData, VideoRead
from app.services.project import ProjectService

SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


@dataclass(frozen=True)
class VideoMetadata:
    fps: float
    duration_seconds: float
    frame_count: int
    width: int
    height: int
    codec: str


def extract_video_metadata(path: Path) -> VideoMetadata:
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError("The file could not be opened as a video.")
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec_value = int(capture.get(cv2.CAP_PROP_FOURCC))
        codec = "".join(chr((codec_value >> (8 * index)) & 0xFF) for index in range(4)).strip(
            "\x00 "
        )
        if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
            raise ValueError("The video has missing or invalid stream metadata.")
        return VideoMetadata(fps, frame_count / fps, frame_count, width, height, codec or "unknown")
    finally:
        capture.release()


class VideoService:
    def __init__(self, session: Session, storage_root: Path) -> None:
        self.repository = VideoRepository(session)
        self.projects = ProjectService(session, storage_root)

    def list_for_project(self, project_id: int) -> list[Video]:
        self.projects.get(project_id)
        return self.repository.list_for_project(project_id)

    def get(self, video_id: int) -> Video:
        video = self.repository.get(video_id)
        if video is None:
            raise AppError("VIDEO_NOT_FOUND", "The requested video does not exist.", 404)
        return video

    def import_uploads(self, project_id: int, uploads: list[UploadFile]) -> VideoImportData:
        project = self.projects.get(project_id)
        video_directory = Path(project.root_path) / "videos"
        video_directory.mkdir(parents=True, exist_ok=True)
        imported: list[VideoRead] = []
        skipped: list[ImportIssue] = []
        errors: list[ImportIssue] = []
        for upload in uploads:
            original_name = Path(upload.filename or "unnamed").name
            extension = Path(original_name).suffix.casefold()
            if extension not in SUPPORTED_VIDEO_EXTENSIONS:
                skipped.append(
                    ImportIssue(
                        filename=original_name,
                        code="UNSUPPORTED_FORMAT",
                        message=f"Unsupported video format: {extension or 'none'}.",
                    )
                )
                continue
            destination = (video_directory / f"{uuid4().hex}{extension}").resolve()
            if not destination.is_relative_to(video_directory.resolve()):
                errors.append(
                    ImportIssue(
                        filename=original_name,
                        code="UNSAFE_PATH",
                        message="The destination path is unsafe.",
                    )
                )
                continue
            try:
                digest = hashlib.sha256()
                size = 0
                with destination.open("xb") as output:
                    while chunk := upload.file.read(1024 * 1024):
                        output.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                content_hash = digest.hexdigest()
                if self.repository.get_by_hash(project_id, content_hash):
                    destination.unlink()
                    skipped.append(
                        ImportIssue(
                            filename=original_name,
                            code="DUPLICATE_VIDEO",
                            message="This video is already imported in the project.",
                        )
                    )
                    continue
                metadata = extract_video_metadata(destination)
                video = self.repository.add(
                    Video(
                        project_id=project_id,
                        filename=original_name,
                        source_path=upload.filename or original_name,
                        stored_path=str(destination),
                        content_hash=content_hash,
                        file_size=size,
                        status="ready",
                        fps=metadata.fps,
                        duration_seconds=metadata.duration_seconds,
                        frame_count=metadata.frame_count,
                        width=metadata.width,
                        height=metadata.height,
                        codec=metadata.codec,
                    )
                )
                imported.append(VideoRead.model_validate(video))
            except (OSError, ValueError) as exc:
                destination.unlink(missing_ok=True)
                errors.append(
                    ImportIssue(
                        filename=original_name, code="VIDEO_IMPORT_FAILED", message=str(exc)
                    )
                )
            finally:
                upload.file.close()
        return VideoImportData(imported=imported, skipped=skipped, errors=errors)

    def delete(self, video_id: int) -> None:
        video = self.get(video_id)
        project = self.projects.get(video.project_id)
        stored_path = Path(video.stored_path).resolve()
        project_root = Path(project.root_path).resolve()
        if not stored_path.is_relative_to(project_root) or not stored_path.is_file():
            if stored_path.exists():
                raise AppError(
                    "UNSAFE_VIDEO_PATH", "The video path is outside project storage.", 409
                )
        self.repository.delete(video)
        if stored_path.is_relative_to(project_root):
            stored_path.unlink(missing_ok=True)
