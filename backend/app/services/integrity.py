from pathlib import Path

from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.extraction import Frame
from app.models.video import Video
from app.schemas.integrity import IntegrityIssue, IntegrityReport
from app.services.frame import generate_thumbnail
from app.services.project import ProjectService


class IntegrityService:
    def __init__(self, session: Session, storage_root: Path) -> None:
        self.session = session
        self.storage_root = storage_root.resolve()
        self.projects = ProjectService(session, storage_root)

    def scan(self, project_id: int, repair_thumbnails: bool) -> IntegrityReport:
        project = self.projects.get(project_id)
        root = Path(project.root_path).resolve()
        issues: list[IntegrityIssue] = []
        if not root.is_relative_to(self.storage_root) or root == self.storage_root:
            issues.append(
                self._issue(
                    "UNSAFE_PROJECT_PATH",
                    "Project path is outside configured storage.",
                    root,
                    "project",
                    project.id,
                    False,
                )
            )
        elif not root.is_dir():
            issues.append(
                self._issue(
                    "PROJECT_DIRECTORY_MISSING",
                    "Project directory is missing.",
                    root,
                    "project",
                    project.id,
                    False,
                )
            )
        videos = list(self.session.scalars(select(Video).where(Video.project_id == project_id)))
        frames = list(self.session.scalars(select(Frame).where(Frame.project_id == project_id)))
        for video in videos:
            stored = Path(video.stored_path).resolve()
            if not stored.is_relative_to(root):
                issues.append(
                    self._issue(
                        "UNSAFE_VIDEO_PATH",
                        "Managed video path leaves project storage.",
                        stored,
                        "video",
                        video.id,
                        False,
                    )
                )
            elif not stored.is_file():
                issues.append(
                    self._issue(
                        "VIDEO_MISSING",
                        "Managed video is missing or was renamed.",
                        stored,
                        "video",
                        video.id,
                        False,
                    )
                )
            if not Path(video.source_path).is_file():
                issues.append(
                    self._issue(
                        "SOURCE_VIDEO_MISSING",
                        "Original source video is no longer available.",
                        Path(video.source_path),
                        "video",
                        video.id,
                        False,
                    )
                )
        for frame in frames:
            image = Path(frame.image_path).resolve()
            if not image.is_relative_to(root):
                issues.append(
                    self._issue(
                        "UNSAFE_FRAME_PATH",
                        "Frame path leaves project storage.",
                        image,
                        "frame",
                        frame.id,
                        False,
                    )
                )
                continue
            if not image.is_file():
                issues.append(
                    self._issue(
                        "FRAME_MISSING",
                        "Extracted frame is missing.",
                        image,
                        "frame",
                        frame.id,
                        False,
                    )
                )
                continue
            thumbnail = (
                Path(frame.thumbnail_path).resolve()
                if frame.thumbnail_path
                else root / "thumbnails" / str(frame.video_id) / f"{frame.id}.jpg"
            )
            valid_thumbnail = thumbnail.is_relative_to(root) and self._valid_image(thumbnail)
            if not valid_thumbnail:
                issue = self._issue(
                    "THUMBNAIL_MISSING",
                    "Thumbnail is missing or invalid.",
                    thumbnail,
                    "frame",
                    frame.id,
                    thumbnail.is_relative_to(root),
                )
                if repair_thumbnails and issue.repairable:
                    generate_thumbnail(image, thumbnail)
                    frame.thumbnail_path = str(thumbnail)
                    issue.repaired = True
                issues.append(issue)
        self.session.commit()
        return IntegrityReport(
            project_id=project_id,
            checked_videos=len(videos),
            checked_frames=len(frames),
            issue_count=len(issues),
            repaired_count=sum(issue.repaired for issue in issues),
            issues=issues,
        )

    @staticmethod
    def _valid_image(path: Path) -> bool:
        try:
            with Image.open(path) as image:
                image.verify()
            return True
        except (FileNotFoundError, OSError, UnidentifiedImageError):
            return False

    @staticmethod
    def _issue(
        code: str,
        message: str,
        path: Path,
        entity_type: str,
        entity_id: int,
        repairable: bool,
    ) -> IntegrityIssue:
        return IntegrityIssue(
            code=code,
            message=message,
            path=str(path),
            entity_type=entity_type,
            entity_id=entity_id,
            repairable=repairable,
        )
