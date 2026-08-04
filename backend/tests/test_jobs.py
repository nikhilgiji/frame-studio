from pathlib import Path

import pytest
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.core.errors import AppError
from app.database.base import Base
from app.database.session import create_database_engine
from app.models.export import ExportJob
from app.models.extraction import ExtractionJob
from app.models.project import Project
from app.models.video import Video
from app.services.jobs import JobService, enforce_job_limit, recover_interrupted_jobs


def test_job_recovery_history_limit_and_clear(tmp_path: Path) -> None:
    engine = create_database_engine(f"sqlite:///{tmp_path / 'jobs.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = Project(name="Jobs", description="", root_path=str(tmp_path / "project"))
        session.add(project)
        session.flush()
        video = Video(
            project_id=project.id,
            filename="jobs.mp4",
            source_path="jobs.mp4",
            stored_path=str(tmp_path / "project" / "videos" / "jobs.mp4"),
            content_hash="1" * 64,
            file_size=1,
            fps=25,
            duration_seconds=1,
            frame_count=25,
            width=640,
            height=480,
            codec="test",
            status="ready",
        )
        session.add(video)
        session.flush()
        session.add(
            ExtractionJob(
                project_id=project.id,
                video_id=video.id,
                mode="every_n_frames",
                mode_value=1,
                output_format="jpeg",
                status="running",
            )
        )
        session.add(
            ExportJob(
                project_id=project.id,
                destination_path=str(tmp_path / "export"),
                export_mode="favorites",
                configuration_json="{}",
                status="pending",
            )
        )
        session.commit()
        assert recover_interrupted_jobs(session) == 2
        history = JobService(session).list(project.id)
        assert len(history) == 2
        assert all(job.status == "interrupted" and job.retryable for job in history)

        session.add_all(
            [
                ExportJob(
                    project_id=project.id,
                    destination_path=str(tmp_path / f"active-{index}"),
                    export_mode="favorites",
                    configuration_json="{}",
                    status="pending",
                )
                for index in range(2)
            ]
        )
        session.commit()
        with pytest.raises(AppError, match="At most 2"):
            enforce_job_limit(session, 2)
        assert JobService(session).clear(project.id) == 2
        assert len(JobService(session).list(project.id)) == 2
    engine.dispose()
