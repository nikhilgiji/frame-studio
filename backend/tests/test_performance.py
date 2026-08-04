from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from fastapi.testclient import TestClient
from sqlalchemy import insert, text
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401
from app.core.config import Settings
from app.database.base import Base
from app.database.session import create_database_engine, get_db
from app.main import create_app
from app.models.extraction import Frame
from app.models.project import Project
from app.models.video import Video


def test_100000_frame_gallery_query_is_bounded_and_indexed(tmp_path: Path) -> None:
    database_path = tmp_path / "performance.db"
    storage = tmp_path / "storage"
    engine = create_database_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    now = datetime.now(UTC)
    with engine.begin() as connection:
        project_id = connection.execute(
            insert(Project).values(name="Large", description="", root_path=str(storage / "large"))
        ).inserted_primary_key[0]
        video_id = connection.execute(
            insert(Video).values(
                project_id=project_id,
                filename="large.mp4",
                source_path="large.mp4",
                stored_path=str(storage / "large" / "videos" / "large.mp4"),
                content_hash="a" * 64,
                file_size=1,
                fps=25,
                duration_seconds=4000,
                frame_count=100000,
                width=640,
                height=480,
                codec="test",
                status="ready",
            )
        ).inserted_primary_key[0]
        batch_size = 2000
        for start in range(0, 100000, batch_size):
            connection.execute(
                insert(Frame),
                [
                    {
                        "project_id": project_id,
                        "video_id": video_id,
                        "frame_number": number,
                        "timestamp_seconds": number / 25,
                        "image_path": str(storage / "large" / "frames" / f"{number}.jpg"),
                        "width": 640,
                        "height": 480,
                        "review_status": "reviewed" if number % 2 else "unreviewed",
                        "favorite": number % 10 == 0,
                        "rejected": False,
                        "created_at": now,
                    }
                    for number in range(start, start + batch_size)
                ],
            )
    app = create_app(Settings(storage_root=storage, database_url=f"sqlite:///{database_path}"))

    def override_db() -> Generator[Session, None, None]:
        with sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        started = perf_counter()
        response = client.get(
            f"/api/v1/projects/{project_id}/frames",
            params={"page": 20, "page_size": 100, "favorite": True},
        )
        elapsed = perf_counter() - started
    data = response.json()
    assert response.status_code == 200
    assert data["total"] == 10000 and len(data["items"]) == 100
    assert elapsed < 1.0
    assert database_path.stat().st_size < 75_000_000
    with engine.connect() as connection:
        plan = " ".join(
            str(row)
            for row in connection.execute(
                text(
                    "EXPLAIN QUERY PLAN SELECT id FROM frames "
                    "WHERE project_id = :project AND favorite = 1 ORDER BY id LIMIT 100"
                ),
                {"project": project_id},
            )
        )
    assert "ix_frames_project_favorite_id" in plan
    engine.dispose()
