from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> list[Project]:
        return list(self.session.scalars(select(Project).order_by(Project.updated_at.desc())))

    def get(self, project_id: int) -> Project | None:
        return self.session.get(Project, project_id)

    def get_by_name(self, name: str) -> Project | None:
        statement = select(Project).where(func.lower(Project.name) == name.casefold())
        return self.session.scalar(statement)

    def add(self, project: Project) -> Project:
        self.session.add(project)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(project)
        return project

    def save(self, project: Project) -> Project:
        self.session.add(project)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.session.delete(project)
        self.session.commit()
