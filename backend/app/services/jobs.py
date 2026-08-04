from datetime import UTC, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.export import ExportJob
from app.models.extraction import ExtractionJob
from app.models.job import MaintenanceJob
from app.schemas.job import UnifiedJobRead

ACTIVE = {"pending", "running", "cancelling"}
FINISHED = {"completed", "cancelled", "failed", "interrupted"}


def enforce_job_limit(session: Session, limit: int) -> None:
    extraction = (
        session.scalar(select(func.count(ExtractionJob.id)).where(ExtractionJob.status.in_(ACTIVE)))
        or 0
    )
    exports = (
        session.scalar(select(func.count(ExportJob.id)).where(ExportJob.status.in_(ACTIVE))) or 0
    )
    maintenance = (
        session.scalar(
            select(func.count(MaintenanceJob.id)).where(MaintenanceJob.status.in_(ACTIVE))
        )
        or 0
    )
    if extraction + exports + maintenance >= limit:
        raise AppError(
            "JOB_CONCURRENCY_LIMIT",
            f"At most {limit} background jobs may run concurrently.",
            409,
        )


def recover_interrupted_jobs(session: Session) -> int:
    message = "Interrupted by an application restart. Retry this job when ready."
    completed = datetime.now(UTC)
    first = (
        session.scalar(select(func.count(ExtractionJob.id)).where(ExtractionJob.status.in_(ACTIVE)))
        or 0
    )
    second = (
        session.scalar(select(func.count(ExportJob.id)).where(ExportJob.status.in_(ACTIVE))) or 0
    )
    third = (
        session.scalar(
            select(func.count(MaintenanceJob.id)).where(MaintenanceJob.status.in_(ACTIVE))
        )
        or 0
    )
    session.execute(
        update(ExtractionJob)
        .where(ExtractionJob.status.in_(ACTIVE))
        .values(status="interrupted", error_message=message, completed_at=completed)
    )
    session.execute(
        update(ExportJob)
        .where(ExportJob.status.in_(ACTIVE))
        .values(status="interrupted", error_message=message, completed_at=completed)
    )
    session.execute(
        update(MaintenanceJob)
        .where(MaintenanceJob.status.in_(ACTIVE))
        .values(status="interrupted", error_message=message, completed_at=completed)
    )
    session.commit()
    return first + second + third


class JobService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, project_id: int) -> list[UnifiedJobRead]:
        extraction = list(
            self.session.scalars(
                select(ExtractionJob).where(ExtractionJob.project_id == project_id)
            )
        )
        exports = list(
            self.session.scalars(select(ExportJob).where(ExportJob.project_id == project_id))
        )
        maintenance = list(
            self.session.scalars(
                select(MaintenanceJob).where(MaintenanceJob.project_id == project_id)
            )
        )
        jobs = (
            [self.from_extraction(job) for job in extraction]
            + [self.from_export(job) for job in exports]
            + [self.from_maintenance(job) for job in maintenance]
        )
        return sorted(jobs, key=lambda job: (job.created_at, job.key), reverse=True)

    def clear(self, project_id: int) -> int:
        extraction = (
            self.session.scalar(
                select(func.count(ExtractionJob.id)).where(
                    ExtractionJob.project_id == project_id,
                    ExtractionJob.status.in_(FINISHED),
                )
            )
            or 0
        )
        exports = (
            self.session.scalar(
                select(func.count(ExportJob.id)).where(
                    ExportJob.project_id == project_id, ExportJob.status.in_(FINISHED)
                )
            )
            or 0
        )
        maintenance = (
            self.session.scalar(
                select(func.count(MaintenanceJob.id)).where(
                    MaintenanceJob.project_id == project_id,
                    MaintenanceJob.status.in_(FINISHED),
                )
            )
            or 0
        )
        self.session.execute(
            delete(ExtractionJob).where(
                ExtractionJob.project_id == project_id,
                ExtractionJob.status.in_(FINISHED),
            )
        )
        self.session.execute(
            delete(ExportJob).where(
                ExportJob.project_id == project_id, ExportJob.status.in_(FINISHED)
            )
        )
        self.session.execute(
            delete(MaintenanceJob).where(
                MaintenanceJob.project_id == project_id,
                MaintenanceJob.status.in_(FINISHED),
            )
        )
        self.session.commit()
        return extraction + exports + maintenance

    def get(self, kind: str, job_id: int) -> ExtractionJob | ExportJob | MaintenanceJob:
        if kind == "extraction":
            job: ExtractionJob | ExportJob | MaintenanceJob | None = self.session.get(
                ExtractionJob, job_id
            )
        elif kind == "export":
            job = self.session.get(ExportJob, job_id)
        elif kind in {"thumbnail", "analysis"}:
            job = self.session.get(MaintenanceJob, job_id)
            if job and job.kind != kind:
                job = None
        else:
            job = None
        if not job:
            raise AppError("JOB_NOT_FOUND", "The requested background job does not exist.", 404)
        return job

    def cancel(self, kind: str, job_id: int) -> ExtractionJob | ExportJob | MaintenanceJob:
        job = self.get(kind, job_id)
        if job.status in {"pending", "running"}:
            job.status = "cancelling"
            self.session.commit()
            self.session.refresh(job)
        return job

    @staticmethod
    def from_extraction(job: ExtractionJob) -> UnifiedJobRead:
        return UnifiedJobRead(
            key=f"extraction:{job.id}",
            id=job.id,
            project_id=job.project_id,
            kind="extraction",
            status=job.status,
            progress=job.progress,
            error_message=job.error_message,
            retryable=job.status in {"failed", "interrupted", "cancelled"},
            created_at=job.created_at,
            completed_at=job.completed_at,
        )

    @staticmethod
    def from_export(job: ExportJob) -> UnifiedJobRead:
        return UnifiedJobRead(
            key=f"export:{job.id}",
            id=job.id,
            project_id=job.project_id,
            kind="export",
            status=job.status,
            progress=job.progress,
            error_message=job.error_message,
            retryable=job.status in {"failed", "interrupted", "cancelled"},
            created_at=job.created_at,
            completed_at=job.completed_at,
        )

    @staticmethod
    def from_maintenance(job: MaintenanceJob) -> UnifiedJobRead:
        return UnifiedJobRead(
            key=f"{job.kind}:{job.id}",
            id=job.id,
            project_id=job.project_id,
            kind=job.kind,
            status=job.status,
            progress=job.progress,
            error_message=job.error_message,
            retryable=job.status in {"failed", "interrupted", "cancelled"},
            created_at=job.created_at,
            completed_at=job.completed_at,
        )
