from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.export import ExportCreate, ExportEnvelope, ExportRead
from app.services.export import ExportService, run_export
from app.services.jobs import enforce_job_limit

router = APIRouter(tags=["exports"])


def service(request: Request, session: Annotated[Session, Depends(get_db)]) -> ExportService:
    return ExportService(session, request.app.state.settings.storage_root)


@router.post("/projects/{project_id}/export-jobs", response_model=ExportEnvelope, status_code=202)
def create_export(
    project_id: int,
    payload: ExportCreate,
    background: BackgroundTasks,
    request: Request,
    exports: Annotated[ExportService, Depends(service)],
) -> ExportEnvelope:
    enforce_job_limit(exports.session, request.app.state.settings.concurrent_job_limit)
    job = exports.create(project_id, payload)
    background.add_task(run_export, job.id, request.app.state.settings.database_url)
    return ExportEnvelope(data=ExportRead.model_validate(job))


@router.get("/export-jobs/{job_id}", response_model=ExportEnvelope)
def get_export(job_id: int, exports: Annotated[ExportService, Depends(service)]) -> ExportEnvelope:
    return ExportEnvelope(data=ExportRead.model_validate(exports.get(job_id)))


@router.post("/export-jobs/{job_id}/cancel", response_model=ExportEnvelope)
def cancel_export(
    job_id: int, exports: Annotated[ExportService, Depends(service)]
) -> ExportEnvelope:
    return ExportEnvelope(data=ExportRead.model_validate(exports.cancel(job_id)))
