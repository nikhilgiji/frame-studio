from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectEnvelope,
    ProjectListEnvelope,
    ProjectRead,
    ProjectUpdate,
)
from app.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def service(request: Request, session: DatabaseSession) -> ProjectService:
    return ProjectService(session, request.app.state.settings.storage_root)


@router.get("", response_model=ProjectListEnvelope)
def list_projects(projects: Annotated[ProjectService, Depends(service)]) -> ProjectListEnvelope:
    return ProjectListEnvelope(data=[ProjectRead.model_validate(item) for item in projects.list()])


@router.post("", response_model=ProjectEnvelope, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, projects: Annotated[ProjectService, Depends(service)]
) -> ProjectEnvelope:
    return ProjectEnvelope(data=ProjectRead.model_validate(projects.create(payload)))


@router.get("/{project_id}", response_model=ProjectEnvelope)
def get_project(
    project_id: int, projects: Annotated[ProjectService, Depends(service)]
) -> ProjectEnvelope:
    return ProjectEnvelope(data=ProjectRead.model_validate(projects.get(project_id)))


@router.patch("/{project_id}", response_model=ProjectEnvelope)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    projects: Annotated[ProjectService, Depends(service)],
) -> ProjectEnvelope:
    return ProjectEnvelope(data=ProjectRead.model_validate(projects.update(project_id, payload)))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int, projects: Annotated[ProjectService, Depends(service)]
) -> Response:
    projects.delete(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
