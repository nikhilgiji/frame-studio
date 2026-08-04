import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from tests.test_review import extracted_frames


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_selected_favorite_and_label_folder_exports_are_safe(
    client: TestClient, tmp_path: Path
) -> None:
    project_id, frames = extracted_frames(client, tmp_path)
    frame_ids = [int(frame["id"]) for frame in frames[:2]]
    label = client.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "Road Vehicle", "shortcut": "V"},
    ).json()["data"]
    client.post(
        "/api/v1/frames/bulk-label",
        json={"frame_ids": frame_ids, "label_ids": [label["id"]]},
    )
    client.patch(f"/api/v1/frames/{frame_ids[0]}/review", json={"favorite": True})
    source_paths = list((tmp_path / "storage" / "projects").glob("**/frames/**/*.jpg"))
    before = {path: digest(path) for path in source_paths}

    selected = client.post(
        f"/api/v1/projects/{project_id}/export-jobs",
        json={
            "destination_name": "selected",
            "export_mode": "selected",
            "frame_ids": frame_ids,
        },
    )
    job = client.get(f"/api/v1/export-jobs/{selected.json()['data']['id']}").json()["data"]
    assert job["status"] == "completed" and job["progress"] == 100
    destination = Path(job["destination_path"])
    manifest = json.loads((destination / "manifest.json").read_text())
    assert len(manifest["frames"]) == 2
    assert len(list((destination / "images").glob("*.jpg"))) == 2

    favorite = client.post(
        f"/api/v1/projects/{project_id}/export-jobs",
        json={"destination_name": "favorites", "export_mode": "favorites"},
    ).json()["data"]
    favorite_job = client.get(f"/api/v1/export-jobs/{favorite['id']}").json()["data"]
    assert (
        len(
            json.loads((Path(favorite_job["destination_path"]) / "manifest.json").read_text())[
                "frames"
            ]
        )
        == 1
    )

    folders = client.post(
        f"/api/v1/projects/{project_id}/export-jobs",
        json={
            "destination_name": "labels",
            "export_mode": "label_folders",
            "label_ids": [label["id"]],
            "multi_label_mode": "copy_each",
            "conflict": "rename",
        },
    ).json()["data"]
    folder_job = client.get(f"/api/v1/export-jobs/{folders['id']}").json()["data"]
    assert len(list((Path(folder_job["destination_path"]) / "Road_Vehicle").glob("*.jpg"))) == 2
    assert {path: digest(path) for path in source_paths} == before


def test_export_can_be_cancelled_before_worker_runs(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    project_id, _frames = extracted_frames(client, tmp_path)
    monkeypatch.setattr("app.api.routes.exports.run_export", lambda _job, _url: None)
    response = client.post(
        f"/api/v1/projects/{project_id}/export-jobs",
        json={"destination_name": "cancel", "export_mode": "manifest"},
    )
    job_id = response.json()["data"]["id"]
    assert (
        client.post(f"/api/v1/export-jobs/{job_id}/cancel").json()["data"]["status"] == "cancelling"
    )


def test_export_path_traversal_is_rejected(client: TestClient, tmp_path: Path) -> None:
    project_id, _frames = extracted_frames(client, tmp_path)
    response = client.post(
        f"/api/v1/projects/{project_id}/export-jobs",
        json={"destination_name": "../outside", "export_mode": "manifest"},
    )
    assert response.status_code == 422
