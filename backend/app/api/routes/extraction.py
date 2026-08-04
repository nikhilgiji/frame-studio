from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.extraction import (
    ExtractionCreate,
    ExtractionEnvelope,
    ExtractionListEnvelope,
    ExtractionRead,
)
from app.services.extraction import ExtractionService, run_extraction

router = APIRouter(tags=["extraction"])


def service(request: Request, session: Annotated[Session, Depends(get_db)]) -> ExtractionService:
    return ExtractionService(session, request.app.state.settings.storage_root)


@router.post(
    "/videos/{video_id}/extraction-jobs", response_model=ExtractionEnvelope, status_code=202
)
def create_job(
    video_id: int,
    payload: ExtractionCreate,
    background: BackgroundTasks,
    request: Request,
    jobs: Annotated[ExtractionService, Depends(service)],
) -> ExtractionEnvelope:
    job = jobs.create(video_id, payload)
    background.add_task(run_extraction, job.id, request.app.state.settings.database_url)
    return ExtractionEnvelope(data=ExtractionRead.model_validate(job))


@router.get("/extraction-jobs/{job_id}", response_model=ExtractionEnvelope)
def get_job(
    job_id: int, jobs: Annotated[ExtractionService, Depends(service)]
) -> ExtractionEnvelope:
    return ExtractionEnvelope(data=ExtractionRead.model_validate(jobs.get(job_id)))


@router.post("/extraction-jobs/{job_id}/cancel", response_model=ExtractionEnvelope)
def cancel_job(
    job_id: int, jobs: Annotated[ExtractionService, Depends(service)]
) -> ExtractionEnvelope:
    return ExtractionEnvelope(data=ExtractionRead.model_validate(jobs.cancel(job_id)))


@router.get("/projects/{project_id}/extraction-jobs", response_model=ExtractionListEnvelope)
def list_jobs(
    project_id: int, jobs: Annotated[ExtractionService, Depends(service)]
) -> ExtractionListEnvelope:
    return ExtractionListEnvelope(
        data=[ExtractionRead.model_validate(job) for job in jobs.list(project_id)]
    )
