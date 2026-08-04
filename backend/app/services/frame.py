from pathlib import Path

from PIL import Image, UnidentifiedImageError
from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.extraction import Frame
from app.models.review import FrameLabel, Label
from app.models.video import Video
from app.schemas.frame import FramePage, FrameQuery, FrameRead
from app.schemas.review import LabelRead
from app.services.project import ProjectService


def generate_thumbnail(image_path: Path, thumbnail_path: Path, max_size: int = 256) -> None:
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = thumbnail_path.with_suffix(".tmp")
    try:
        with Image.open(image_path) as image:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            image.convert("RGB").save(temporary, format="JPEG", quality=82, optimize=True)
        temporary.replace(thumbnail_path)
    finally:
        temporary.unlink(missing_ok=True)


class FrameService:
    def __init__(self, session: Session, storage_root: Path) -> None:
        self.session = session
        self.projects = ProjectService(session, storage_root)

    def get(self, frame_id: int) -> Frame:
        frame = self.session.get(Frame, frame_id)
        if not frame:
            raise AppError("FRAME_NOT_FOUND", "The requested frame does not exist.", 404)
        return frame

    def list(self, project_id: int, query: FrameQuery) -> FramePage:
        self.projects.get(project_id)
        filters = [Frame.project_id == project_id]
        if query.video_id is not None:
            filters.append(Frame.video_id == query.video_id)
        if query.review_status is not None:
            filters.append(Frame.review_status == query.review_status)
        if query.favorite is not None:
            filters.append(Frame.favorite == query.favorite)
        if query.rejected is not None:
            filters.append(Frame.rejected == query.rejected)
        if query.frame_number is not None:
            filters.append(Frame.frame_number == query.frame_number)
        if query.timestamp_min is not None:
            filters.append(Frame.timestamp_seconds >= query.timestamp_min)
        if query.timestamp_max is not None:
            filters.append(Frame.timestamp_seconds <= query.timestamp_max)
        if query.unlabeled:
            filters.append(
                ~exists(select(FrameLabel.frame_id).where(FrameLabel.frame_id == Frame.id))
            )
        for label_id in query.label_ids:
            filters.append(
                exists(
                    select(FrameLabel.frame_id).where(
                        FrameLabel.frame_id == Frame.id, FrameLabel.label_id == label_id
                    )
                )
            )
        if query.search:
            pattern = f"%{query.search}%"
            search_filters = [
                Frame.image_path.ilike(pattern),
                exists(
                    select(Video.id).where(
                        Video.id == Frame.video_id, Video.filename.ilike(pattern)
                    )
                ),
            ]
            if query.search.isdigit():
                search_filters.append(Frame.frame_number == int(query.search))
            filters.append(or_(*search_filters))
        total = self.session.scalar(select(func.count(Frame.id)).where(*filters)) or 0
        sort_columns = {
            "frame_number": Frame.frame_number,
            "timestamp_seconds": Frame.timestamp_seconds,
            "created_at": Frame.created_at,
        }
        sort_column = sort_columns.get(query.sort_by, Frame.frame_number)
        order = sort_column.desc() if query.sort_order == "desc" else sort_column.asc()
        statement = (
            select(Frame)
            .where(*filters)
            .order_by(order, Frame.id.asc())
            .offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )
        items = [self.serialize(frame) for frame in self.session.scalars(statement)]
        return FramePage(
            items=items,
            page=query.page,
            page_size=query.page_size,
            total=total,
            has_next=query.page * query.page_size < total,
        )

    def serialize(self, frame: Frame) -> FrameRead:
        labels = list(
            self.session.scalars(
                select(Label)
                .join(FrameLabel)
                .where(FrameLabel.frame_id == frame.id)
                .order_by(Label.position)
            )
        )
        data = FrameRead.model_validate(frame)
        video = self.session.get(Video, frame.video_id)
        data.video_filename = video.filename if video else "Missing video"
        data.labels = [LabelRead.model_validate(label) for label in labels]
        return data

    def image(self, frame_id: int) -> Path:
        frame = self.get(frame_id)
        path = self._safe_path(frame, Path(frame.image_path))
        if not path.is_file():
            raise AppError("FRAME_IMAGE_MISSING", "The full-resolution frame is missing.", 404)
        return path

    def thumbnail(self, frame_id: int) -> Path:
        frame = self.get(frame_id)
        image_path = self.image(frame_id)
        path = (
            Path(frame.thumbnail_path)
            if frame.thumbnail_path
            else (
                image_path.parent.parent.parent
                / "thumbnails"
                / str(frame.video_id)
                / f"{frame.id}.jpg"
            )
        )
        path = self._safe_path(frame, path)
        try:
            with Image.open(path) as thumbnail:
                thumbnail.verify()
        except (FileNotFoundError, OSError, UnidentifiedImageError):
            generate_thumbnail(image_path, path)
        if frame.thumbnail_path != str(path):
            frame.thumbnail_path = str(path)
            self.session.commit()
        return path

    def _safe_path(self, frame: Frame, path: Path) -> Path:
        project = self.projects.get(frame.project_id)
        root, resolved = Path(project.root_path).resolve(), path.resolve()
        if not resolved.is_relative_to(root):
            raise AppError("UNSAFE_FRAME_PATH", "The frame path is outside project storage.", 409)
        return resolved
