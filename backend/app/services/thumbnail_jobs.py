from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import create_database_engine
from app.models.extraction import Frame
from app.models.job import MaintenanceJob
from app.services.frame import FrameService
from app.services.project import ProjectService


def create_thumbnail_job(session: Session, project_id: int, storage_root: Path) -> MaintenanceJob:
    ProjectService(session, storage_root).get(project_id)
    job = MaintenanceJob(
        project_id=project_id,
        kind="thumbnail",
        configuration_json="{}",
        status="pending",
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def run_thumbnail_job(job_id: int, database_url: str, storage_root: str) -> None:
    engine = create_database_engine(database_url)
    with Session(engine) as session:
        job = session.get(MaintenanceJob, job_id)
        if not job:
            return
        job.status = "running"
        session.commit()
        try:
            frame_ids = list(
                session.scalars(
                    select(Frame.id).where(Frame.project_id == job.project_id).order_by(Frame.id)
                )
            )
            frames = FrameService(session, Path(storage_root))
            for index, frame_id in enumerate(frame_ids, 1):
                session.refresh(job)
                if job.status == "cancelling":
                    job.status = "cancelled"
                    job.completed_at = datetime.now(UTC)
                    session.commit()
                    return
                frames.thumbnail(frame_id)
                job.progress = index / max(1, len(frame_ids)) * 100
                session.commit()
            job.status = "completed"
            job.progress = 100
            job.completed_at = datetime.now(UTC)
            session.commit()
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
            job.completed_at = datetime.now(UTC)
            session.commit()
    engine.dispose()
