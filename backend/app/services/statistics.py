from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.core.errors import AppError
from app.models.export import ExportJob
from app.models.extraction import ExtractionJob, Frame
from app.models.project import Project
from app.models.review import FrameLabel, Label
from app.models.video import Video
from app.schemas.statistics import DatedCount, NamedCount, ProjectStatistics


class StatisticsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def project(
        self,
        project_id: int,
        video_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> ProjectStatistics:
        if self.session.get(Project, project_id) is None:
            raise AppError("PROJECT_NOT_FOUND", "The requested project does not exist.", 404)
        frame_filters = [Frame.project_id == project_id]
        if video_id is not None:
            frame_filters.append(Frame.video_id == video_id)
        if date_from is not None:
            frame_filters.append(Frame.created_at >= date_from)
        if date_to is not None:
            frame_filters.append(Frame.created_at < date_to)

        def count(*extra: ColumnElement[bool]) -> int:
            return (
                self.session.scalar(select(func.count(Frame.id)).where(*frame_filters, *extra)) or 0
            )

        label_rows = self.session.execute(
            select(Label.id, Label.name, func.count(FrameLabel.frame_id))
            .outerjoin(FrameLabel, FrameLabel.label_id == Label.id)
            .outerjoin(Frame, Frame.id == FrameLabel.frame_id)
            .where(Label.project_id == project_id, *frame_filters)
            .group_by(Label.id, Label.name)
            .order_by(Label.position, Label.id)
        ).all()
        video_rows = self.session.execute(
            select(Video.id, Video.filename, func.count(Frame.id))
            .outerjoin(Frame, Frame.video_id == Video.id)
            .where(Video.project_id == project_id, *frame_filters)
            .group_by(Video.id, Video.filename)
            .order_by(Video.id)
        ).all()
        progress_rows = self.session.execute(
            select(func.date(Frame.reviewed_at), func.count(Frame.id))
            .where(*frame_filters, Frame.reviewed_at.is_not(None))
            .group_by(func.date(Frame.reviewed_at))
            .order_by(func.date(Frame.reviewed_at))
        ).all()
        return ProjectStatistics(
            total_projects=self.session.scalar(select(func.count(Project.id))) or 0,
            total_videos=self.session.scalar(
                select(func.count(Video.id)).where(Video.project_id == project_id)
            )
            or 0,
            total_frames=count(),
            reviewed_frames=count(Frame.review_status == "reviewed"),
            unreviewed_frames=count(Frame.review_status == "unreviewed"),
            rejected_frames=count(Frame.rejected.is_(True)),
            favorite_frames=count(Frame.favorite.is_(True)),
            extraction_jobs=self.session.scalar(
                select(func.count(ExtractionJob.id)).where(ExtractionJob.project_id == project_id)
            )
            or 0,
            export_jobs=self.session.scalar(
                select(func.count(ExportJob.id)).where(ExportJob.project_id == project_id)
            )
            or 0,
            frames_per_label=[
                NamedCount(id=row[0], name=row[1], count=row[2]) for row in label_rows
            ],
            frames_per_video=[
                NamedCount(id=row[0], name=row[1], count=row[2]) for row in video_rows
            ],
            review_progress=[
                DatedCount(date=date.fromisoformat(row[0]), count=row[1])
                for row in progress_rows
                if row[0]
            ],
        )
