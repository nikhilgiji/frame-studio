from fastapi.testclient import TestClient

from app.main import create_app


def test_packaged_frontend_and_spa_routes_are_served() -> None:
    with TestClient(create_app()) as client:
        home = client.get("/")
        route = client.get("/projects/42/gallery")
        missing_api = client.get("/api/v1/not-a-route")
        missing_asset = client.get("/assets/not-a-file.js")

    assert home.status_code == 200
    assert "Frame Studio" in home.text
    assert route.status_code == 200
    assert route.text == home.text
    assert missing_api.status_code == 404
    assert missing_asset.status_code == 404
