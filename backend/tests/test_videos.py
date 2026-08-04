from pathlib import Path

import cv2
import numpy as np
from fastapi.testclient import TestClient


def make_video(path: Path, frame_count: int = 12, fps: float = 6.0) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, (64, 48))
    assert writer.isOpened()
    for index in range(frame_count):
        frame = np.full((48, 64, 3), index * 10, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def project_id(client: TestClient) -> int:
    response = client.post("/api/v1/projects", json={"name": "Video Project"})
    return int(response.json()["data"]["id"])


def test_import_lists_metadata_and_deletes_video(client: TestClient, tmp_path: Path) -> None:
    source = tmp_path / "clip.avi"
    make_video(source)
    pid = project_id(client)
    with source.open("rb") as video_file:
        response = client.post(
            f"/api/v1/projects/{pid}/videos/import",
            files={"files": ("clip.avi", video_file, "video/x-msvideo")},
        )

    assert response.status_code == 200
    video = response.json()["data"]["imported"][0]
    assert video["filename"] == "clip.avi"
    assert video["frame_count"] == 12
    assert video["fps"] == 6.0
    assert video["duration_seconds"] == 2.0
    assert video["width"] == 64 and video["height"] == 48
    stored_path = Path(video["stored_path"])
    assert stored_path.is_file() and stored_path != source

    assert client.get(f"/api/v1/videos/{video['id']}").json()["data"]["codec"]
    assert len(client.get(f"/api/v1/projects/{pid}/videos").json()["data"]) == 1
    assert client.delete(f"/api/v1/videos/{video['id']}").status_code == 204
    assert not stored_path.exists()
    assert source.exists()


def test_multiple_import_skips_unsupported_duplicate_and_reports_corrupt(
    client: TestClient, tmp_path: Path
) -> None:
    source = tmp_path / "valid.avi"
    make_video(source, frame_count=5)
    content = source.read_bytes()
    pid = project_id(client)
    response = client.post(
        f"/api/v1/projects/{pid}/videos/import",
        files=[
            ("files", ("valid.avi", content, "video/x-msvideo")),
            ("files", ("duplicate.avi", content, "video/x-msvideo")),
            ("files", ("notes.txt", b"not video", "text/plain")),
            ("files", ("corrupt.mp4", b"broken", "video/mp4")),
        ],
    )

    data = response.json()["data"]
    assert len(data["imported"]) == 1
    assert {item["code"] for item in data["skipped"]} == {
        "DUPLICATE_VIDEO",
        "UNSUPPORTED_FORMAT",
    }
    assert data["errors"][0]["code"] == "VIDEO_IMPORT_FAILED"
    assert "opened" in data["errors"][0]["message"] or "metadata" in data["errors"][0]["message"]
