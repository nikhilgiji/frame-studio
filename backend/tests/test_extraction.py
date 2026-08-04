from pathlib import Path

import cv2
from fastapi.testclient import TestClient
from PIL import Image

from app.services.extraction import sampling_indices
from tests.test_videos import make_video


def imported_video(client: TestClient, tmp_path: Path) -> dict[str, object]:
    project = client.post("/api/v1/projects", json={"name": "Extract"}).json()["data"]
    source = tmp_path / "extract.avi"
    make_video(source, frame_count=12, fps=6)
    with source.open("rb") as stream:
        response = client.post(
            f"/api/v1/projects/{project['id']}/videos/import",
            files={"files": ("extract.avi", stream, "video/x-msvideo")},
        )
    return response.json()["data"]["imported"][0]


def test_sampling_calculations() -> None:
    assert sampling_indices(21, 10, "every_n_frames", 10) == [0, 10, 20]
    assert sampling_indices(21, 10, "frames_per_second", 2) == [0, 5, 10, 15, 20]
    assert sampling_indices(21, 10, "every_n_seconds", 2) == [0, 20]


def test_extraction_job_writes_readable_frames_and_prevents_duplicates(
    client: TestClient, tmp_path: Path
) -> None:
    video = imported_video(client, tmp_path)
    payload = {
        "mode": "every_n_frames",
        "mode_value": 4,
        "output_format": "jpeg",
        "jpeg_quality": 85,
        "resize_width": 32,
    }
    response = client.post(f"/api/v1/videos/{video['id']}/extraction-jobs", json=payload)
    assert response.status_code == 202
    job_id = response.json()["data"]["id"]
    job = client.get(f"/api/v1/extraction-jobs/{job_id}").json()["data"]
    assert job["status"] == "completed"
    assert job["processed_frames"] == job["total_frames"] == 3
    assert job["progress"] == 100

    frame_dir = Path(str(video["stored_path"])).parent.parent / "frames" / str(video["id"])
    images = sorted(frame_dir.glob("*.jpg"))
    assert len(images) == 3
    assert cv2.imread(str(images[0])).shape[:2] == (24, 32)
    thumbnail = client.get("/api/v1/frames/1/thumbnail")
    assert thumbnail.status_code == 200
    with Image.open(
        Path(str(video["stored_path"])).parent.parent / "thumbnails" / str(video["id"]) / "1.jpg"
    ) as thumb:
        assert thumb.width <= 256 and thumb.height <= 256
        thumbnail_path = Path(thumb.filename)
    thumbnail_path.unlink()
    regenerated = client.get("/api/v1/frames/1/thumbnail")
    assert regenerated.status_code == 200 and thumbnail_path.is_file()
    assert client.get("/api/v1/frames/1/image").status_code == 200
    page = client.get(f"/api/v1/projects/{video['project_id']}/frames?page=1&page_size=2").json()
    assert page["total"] == 3 and len(page["items"]) == 2 and page["has_next"] is True
    assert [item["frame_number"] for item in page["items"]] == [0, 4]

    duplicate = client.post(f"/api/v1/videos/{video['id']}/extraction-jobs", json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "EXTRACTION_EXISTS"

    payload["overwrite"] = True
    payload["mode"] = "frames_per_second"
    payload["mode_value"] = 3
    overwritten = client.post(f"/api/v1/videos/{video['id']}/extraction-jobs", json=payload)
    assert overwritten.status_code == 202
    final = client.get(f"/api/v1/extraction-jobs/{overwritten.json()['data']['id']}").json()["data"]
    assert final["status"] == "completed"
    assert final["processed_frames"] == 6

    payload["mode"] = "every_n_seconds"
    payload["mode_value"] = 1
    seconds_job = client.post(f"/api/v1/videos/{video['id']}/extraction-jobs", json=payload).json()[
        "data"
    ]
    seconds_final = client.get(f"/api/v1/extraction-jobs/{seconds_job['id']}").json()["data"]
    assert seconds_final["status"] == "completed"
    assert seconds_final["processed_frames"] == 2


def test_pending_extraction_can_be_cancelled(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    video = imported_video(client, tmp_path)
    monkeypatch.setattr("app.api.routes.extraction.run_extraction", lambda _job, _url: None)
    response = client.post(
        f"/api/v1/videos/{video['id']}/extraction-jobs",
        json={"mode": "every_n_seconds", "mode_value": 2},
    )
    job_id = response.json()["data"]["id"]
    cancelled = client.post(f"/api/v1/extraction-jobs/{job_id}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["data"]["status"] == "cancelling"
