from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401
from app.core.config import Settings
from app.database.base import Base
from app.database.session import create_database_engine, get_db
from app.main import create_app


def make_client(database_path: Path, storage_root: Path) -> tuple[TestClient, Engine]:
    engine = create_database_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    app = create_app(Settings(storage_root=storage_root))

    def override_db() -> Generator[Session, None, None]:
        with sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    return TestClient(app), engine


def test_projects_survive_application_restart(tmp_path: Path) -> None:
    database_path = tmp_path / "persistent.db"
    storage_root = tmp_path / "storage"
    first_client, first_engine = make_client(database_path, storage_root)
    with first_client:
        assert first_client.post("/api/v1/projects", json={"name": "Persistent"}).status_code == 201
    first_engine.dispose()

    restarted_client, restarted_engine = make_client(database_path, storage_root)
    with restarted_client:
        response = restarted_client.get("/api/v1/projects")
    restarted_engine.dispose()

    assert response.status_code == 200
    assert [project["name"] for project in response.json()["data"]] == ["Persistent"]
