from typing import Annotated, Literal, cast

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.database.session import get_db
from app.models.export import ExportJob
from app.models.extraction import ExtractionJob
from app.models.job import MaintenanceJob
from app.schemas.export import ExportCreate
from app.schemas.extraction import ExtractionCreate
from app.schemas.job import (
    ClearJobsEnvelope,
    ClearJobsResult,
    RetryJobEnvelope,
    UnifiedJobListEnvelope,
)
from app.services.export import ExportService, run_export
from app.services.extraction import ExtractionService, run_extraction
from app.services.jobs import JobService, enforce_job_limit
from app.services.thumbnail_jobs import create_thumbnail_job, run_thumbnail_job

router = APIRouter(tags=["background jobs"])


@router.post(
    "/projects/{project_id}/thumbnail-jobs",
    response_model=RetryJobEnvelope,
    status_code=202,
)
def create_thumbnails(
    project_id: int,
    background: BackgroundTasks,
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> RetryJobEnvelope:
    enforce_job_limit(session, request.app.state.settings.concurrent_job_limit)
    job = create_thumbnail_job(session, project_id, request.app.state.settings.storage_root)
    background.add_task(
        run_thumbnail_job,
        job.id,
        request.app.state.settings.database_url,
        str(request.app.state.settings.storage_root),
    )
    return RetryJobEnvelope(data=JobService(session).from_maintenance(job))


@router.get("/projects/{project_id}/jobs", response_model=UnifiedJobListEnvelope)
def list_jobs(
    project_id: int, session: Annotated[Session, Depends(get_db)]
) -> UnifiedJobListEnvelope:
    return UnifiedJobListEnvelope(data=JobService(session).list(project_id))


@router.post("/jobs/{kind}/{job_id}/retry", response_model=RetryJobEnvelope, status_code=202)
def retry_job(
    kind: str,
    job_id: int,
    background: BackgroundTasks,
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> RetryJobEnvelope:
    jobs = JobService(session)
    previous = jobs.get(kind, job_id)
    if previous.status not in {"failed", "interrupted", "cancelled"}:
        raise AppError("JOB_NOT_RETRYABLE", "Only failed or interrupted jobs can be retried.", 409)
    enforce_job_limit(session, request.app.state.settings.concurrent_job_limit)
    if isinstance(previous, ExtractionJob):
        payload = ExtractionCreate(
            mode=cast(
                Literal["every_n_frames", "frames_per_second", "every_n_seconds"],
                previous.mode,
            ),
            mode_value=previous.mode_value,
            output_format=cast(Literal["jpeg", "png"], previous.output_format),
            jpeg_quality=previous.jpeg_quality,
            resize_width=previous.resize_width,
            resize_height=previous.resize_height,
            overwrite=True,
        )
        created = ExtractionService(session, request.app.state.settings.storage_root).create(
            previous.video_id, payload
        )
        background.add_task(run_extraction, created.id, request.app.state.settings.database_url)
        return RetryJobEnvelope(data=jobs.from_extraction(created))
    if isinstance(previous, ExportJob):
        created_export = ExportService(session, request.app.state.settings.storage_root).create(
            previous.project_id, ExportCreate.model_validate_json(previous.configuration_json)
        )
        background.add_task(run_export, created_export.id, request.app.state.settings.database_url)
        return RetryJobEnvelope(data=jobs.from_export(created_export))
    assert isinstance(previous, MaintenanceJob)
    created_maintenance = create_thumbnail_job(
        session, previous.project_id, request.app.state.settings.storage_root
    )
    background.add_task(
        run_thumbnail_job,
        created_maintenance.id,
        request.app.state.settings.database_url,
        str(request.app.state.settings.storage_root),
    )
    return RetryJobEnvelope(data=jobs.from_maintenance(created_maintenance))


@router.post("/jobs/{kind}/{job_id}/cancel", response_model=RetryJobEnvelope)
def cancel_job(
    kind: str,
    job_id: int,
    session: Annotated[Session, Depends(get_db)],
) -> RetryJobEnvelope:
    jobs = JobService(session)
    job = jobs.cancel(kind, job_id)
    if isinstance(job, ExtractionJob):
        data = jobs.from_extraction(job)
    elif isinstance(job, ExportJob):
        data = jobs.from_export(job)
    else:
        data = jobs.from_maintenance(job)
    return RetryJobEnvelope(data=data)


@router.delete("/projects/{project_id}/jobs/completed", response_model=ClearJobsEnvelope)
def clear_jobs(project_id: int, session: Annotated[Session, Depends(get_db)]) -> ClearJobsEnvelope:
    return ClearJobsEnvelope(
        data=ClearJobsResult(cleared_count=JobService(session).clear(project_id))
    )
