from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.video import Video


class VideoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_project(self, project_id: int) -> list[Video]:
        statement = (
            select(Video).where(Video.project_id == project_id).order_by(Video.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def get(self, video_id: int) -> Video | None:
        return self.session.get(Video, video_id)

    def get_by_hash(self, project_id: int, content_hash: str) -> Video | None:
        statement = select(Video).where(
            Video.project_id == project_id, Video.content_hash == content_hash
        )
        return self.session.scalar(statement)

    def add(self, video: Video) -> Video:
        self.session.add(video)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(video)
        return video

    def delete(self, video: Video) -> None:
        self.session.delete(video)
        self.session.commit()
