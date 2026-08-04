import re
from pathlib import Path
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, session: Session, storage_root: Path) -> None:
        self.repository = ProjectRepository(session)
        self.storage_root = storage_root.resolve()

    def list(self) -> list[Project]:
        return self.repository.list()

    def get(self, project_id: int) -> Project:
        project = self.repository.get(project_id)
        if project is None:
            raise AppError("PROJECT_NOT_FOUND", "The requested project does not exist.", 404)
        return project

    def create(self, payload: ProjectCreate) -> Project:
        self._ensure_unique_name(payload.name)
        project_directory = self._new_project_directory(payload.name)
        project_directory.mkdir(parents=True, exist_ok=False)
        project = Project(
            name=payload.name,
            description=payload.description,
            root_path=str(project_directory),
        )
        try:
            return self.repository.add(project)
        except IntegrityError as exc:
            # The directory is known to be newly-created and empty here.
            project_directory.rmdir()
            raise AppError(
                "PROJECT_NAME_EXISTS", "A project with this name already exists.", 409
            ) from exc

    def update(self, project_id: int, payload: ProjectUpdate) -> Project:
        project = self.get(project_id)
        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates and updates["name"] != project.name:
            self._ensure_unique_name(updates["name"], exclude_id=project_id)
        for field, value in updates.items():
            setattr(project, field, value)
        try:
            return self.repository.save(project)
        except IntegrityError as exc:
            raise AppError(
                "PROJECT_NAME_EXISTS", "A project with this name already exists.", 409
            ) from exc

    def delete(self, project_id: int) -> None:
        project = self.get(project_id)
        self._validate_managed_path(Path(project.root_path))
        self.repository.delete(project)

    def _ensure_unique_name(self, name: str, exclude_id: int | None = None) -> None:
        existing = self.repository.get_by_name(name)
        if existing is not None and existing.id != exclude_id:
            raise AppError("PROJECT_NAME_EXISTS", "A project with this name already exists.", 409)

    def _new_project_directory(self, name: str) -> Path:
        self.storage_root.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-") or "project"
        candidate = (self.storage_root / "projects" / f"{slug}-{uuid4().hex[:8]}").resolve()
        self._validate_managed_path(candidate)
        return candidate

    def _validate_managed_path(self, path: Path) -> None:
        resolved = path.resolve()
        if not resolved.is_relative_to(self.storage_root) or resolved == self.storage_root:
            raise AppError(
                "UNSAFE_PROJECT_PATH", "The project path is outside managed storage.", 409
            )
