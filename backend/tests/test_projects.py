from pathlib import Path

from fastapi.testclient import TestClient


def create_project(client: TestClient, name: str = "Road Dataset") -> dict[str, object]:
    response = client.post("/api/v1/projects", json={"name": name, "description": "Dashcam"})
    assert response.status_code == 201
    return response.json()["data"]


def test_project_crud_and_directory_creation(client: TestClient) -> None:
    first = create_project(client)
    second = create_project(client, "Warehouse")
    third = create_project(client, "Pedestrians")

    assert Path(str(first["root_path"])).is_dir()
    assert len({first["root_path"], second["root_path"], third["root_path"]}) == 3

    renamed = client.patch(f"/api/v1/projects/{second['id']}", json={"name": "Indoor Warehouse"})
    assert renamed.status_code == 200
    assert renamed.json()["data"]["name"] == "Indoor Warehouse"
    assert renamed.json()["data"]["updated_at"]

    fetched = client.get(f"/api/v1/projects/{first['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["data"]["created_at"]

    deleted = client.delete(f"/api/v1/projects/{third['id']}")
    assert deleted.status_code == 204
    listed = client.get("/api/v1/projects")
    assert listed.status_code == 200
    assert {project["name"] for project in listed.json()["data"]} == {
        "Road Dataset",
        "Indoor Warehouse",
    }


def test_duplicate_names_are_clear_and_case_insensitive(client: TestClient) -> None:
    create_project(client, "Road Dataset")
    response = client.post("/api/v1/projects", json={"name": "road dataset"})

    assert response.status_code == 409
    assert response.json() == {
        "data": None,
        "error": {
            "code": "PROJECT_NAME_EXISTS",
            "message": "A project with this name already exists.",
        },
    }


def test_not_found_error_is_structured(client: TestClient) -> None:
    response = client.get("/api/v1/projects/999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROJECT_NOT_FOUND"


def test_delete_does_not_remove_project_files(client: TestClient) -> None:
    project = create_project(client)
    project_path = Path(str(project["root_path"]))
    marker = project_path / "source-video.mp4"
    marker.write_bytes(b"source")

    assert client.delete(f"/api/v1/projects/{project['id']}").status_code == 204
    assert marker.read_bytes() == b"source"
