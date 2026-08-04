from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health_endpoint(tmp_path: Path) -> None:
    settings = Settings(storage_root=tmp_path, cors_origins=["http://localhost:3000"])
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert tmp_path.exists()


def test_cors_allows_configured_frontend(tmp_path: Path) -> None:
    settings = Settings(storage_root=tmp_path, cors_origins=["http://localhost:3000"])
    with TestClient(create_app(settings)) as client:
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
