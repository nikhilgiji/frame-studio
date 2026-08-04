from pathlib import Path

from fastapi.testclient import TestClient

from tests.test_extraction import imported_video


def extracted_frames(client: TestClient, tmp_path: Path) -> tuple[int, list[dict[str, object]]]:
    video = imported_video(client, tmp_path)
    client.post(
        f"/api/v1/videos/{video['id']}/extraction-jobs",
        json={"mode": "every_n_frames", "mode_value": 2},
    )
    project_id = int(video["project_id"])
    frames = client.get(f"/api/v1/projects/{project_id}/frames").json()["items"]
    return project_id, frames


def test_labels_bulk_review_filters_and_session_persist(client: TestClient, tmp_path: Path) -> None:
    project_id, frames = extracted_frames(client, tmp_path)
    labels = []
    for index, name in enumerate(["Vehicle", "Pedestrian", "Rain", "Night", "Empty"]):
        response = client.post(
            f"/api/v1/projects/{project_id}/labels",
            json={"name": name, "shortcut": str(index + 1), "color": "#44aa88"},
        )
        assert response.status_code == 201
        labels.append(response.json()["data"])
    conflict = client.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "Conflict", "shortcut": "1"},
    )
    assert conflict.status_code == 409 and conflict.json()["error"]["code"] == "LABEL_CONFLICT"
    moved = client.patch(f"/api/v1/labels/{labels[4]['id']}", json={"position": 0})
    assert moved.status_code == 200
    ordered = client.get(f"/api/v1/projects/{project_id}/labels").json()["data"]
    assert ordered[0]["name"] == "Empty"

    frame_id = int(frames[0]["id"])
    assigned = client.post(
        f"/api/v1/frames/{frame_id}/labels",
        json={"label_ids": [labels[0]["id"], labels[1]["id"]]},
    )
    assert {label["name"] for label in assigned.json()["data"]["labels"]} == {
        "Vehicle",
        "Pedestrian",
    }
    frame_ids = [int(frame["id"]) for frame in frames]
    assert (
        client.post(
            "/api/v1/frames/bulk-label",
            json={"frame_ids": frame_ids, "label_ids": [labels[2]["id"]], "action": "assign"},
        ).status_code
        == 204
    )
    assert (
        client.post(
            "/api/v1/frames/bulk-review",
            json={"frame_ids": frame_ids, "review_status": "reviewed", "favorite": True},
        ).status_code
        == 204
    )

    filtered = client.get(
        f"/api/v1/projects/{project_id}/frames",
        params={"label_ids": labels[2]["id"], "review_status": "reviewed", "favorite": True},
    ).json()
    assert filtered["total"] == len(frame_ids)
    filtered_label = client.post(
        f"/api/v1/projects/{project_id}/frames/bulk-label",
        json={
            "all_filtered": True,
            "filters": {"favorite": True},
            "label_ids": [labels[3]["id"]],
            "action": "assign",
        },
    )
    assert filtered_label.json()["data"]["affected_count"] == len(frame_ids)
    filtered_reject = client.post(
        f"/api/v1/projects/{project_id}/frames/bulk-review",
        json={
            "all_filtered": True,
            "filters": {"label_ids": [labels[3]["id"]]},
            "rejected": True,
        },
    )
    assert filtered_reject.json()["data"]["affected_count"] == len(frame_ids)
    queue = client.post(
        f"/api/v1/projects/{project_id}/review-queues",
        json={
            "name": "Favorite review",
            "queue_type": "filtered",
            "filters": {"favorite": True},
        },
    ).json()["data"]
    assert queue["total"] == len(frame_ids) and queue["reviewed"] == len(frame_ids)
    resumed = client.patch(f"/api/v1/review-queues/{queue['id']}", json={"position": 3}).json()[
        "data"
    ]
    assert resumed["position"] == 3 and resumed["current_frame_id"] == frame_ids[3]
    client.delete(f"/api/v1/frames/{frame_id}/labels/{labels[1]['id']}")
    stable = client.get(f"/api/v1/review-queues/{queue['id']}").json()["data"]
    assert stable["total"] == len(frame_ids) and stable["position"] == 3
    statistics = client.get(f"/api/v1/projects/{project_id}/statistics").json()["data"]
    assert statistics["total_frames"] == len(frame_ids)
    assert statistics["reviewed_frames"] == len(frame_ids)
    assert statistics["favorite_frames"] == len(frame_ids)
    assert statistics["rejected_frames"] == len(frame_ids)
    assert sum(row["count"] for row in statistics["frames_per_video"]) == len(frame_ids)
    assert statistics["extraction_jobs"] >= 1
    client.post(
        f"/api/v1/projects/{project_id}/frames/bulk-review",
        json={
            "all_filtered": True,
            "filters": {"favorite": True},
            "favorite": False,
        },
    )
    actions = client.get(f"/api/v1/projects/{project_id}/action-history").json()["data"]
    assert actions[0]["description"] == f"Updated review state for {len(frame_ids)} frames"
    undone = client.post(f"/api/v1/projects/{project_id}/action-history/undo")
    assert undone.json()["data"]["status"] == "undone"
    assert client.get(f"/api/v1/projects/{project_id}/frames", params={"favorite": True}).json()[
        "total"
    ] == len(frame_ids)
    redone = client.post(f"/api/v1/projects/{project_id}/action-history/redo")
    assert redone.json()["data"]["status"] == "applied"
    assert (
        client.get(f"/api/v1/projects/{project_id}/frames", params={"favorite": True}).json()[
            "total"
        ]
        == 0
    )
    searched = client.get(
        f"/api/v1/projects/{project_id}/frames", params={"search": "extract.avi"}
    ).json()
    assert searched["total"] == len(frame_ids)
    exact = client.get(f"/api/v1/projects/{project_id}/frames", params={"frame_number": 4}).json()
    assert exact["total"] == 1 and exact["items"][0]["frame_number"] == 4
    ranged = client.get(
        f"/api/v1/projects/{project_id}/frames",
        params={"timestamp_min": 1, "timestamp_max": 1.5},
    ).json()
    assert all(1 <= item["timestamp_seconds"] <= 1.5 for item in ranged["items"])
    assert client.delete(f"/api/v1/frames/{frame_id}/labels/{labels[0]['id']}").status_code == 200
    unlabeled = client.get(
        f"/api/v1/projects/{project_id}/frames", params={"unlabeled": True}
    ).json()
    assert unlabeled["total"] == 0

    session_payload = {
        "last_frame_id": frame_id,
        "active_filters": {"favorite": True},
        "gallery_position": 42,
        "thumbnail_size": 220,
    }
    saved = client.patch(f"/api/v1/projects/{project_id}/review-session", json=session_payload)
    assert saved.status_code == 200
    restored = client.get(f"/api/v1/projects/{project_id}/review-session").json()["data"]
    assert restored["last_frame_id"] == frame_id
    assert restored["active_filters"] == {"favorite": True}
    assert restored["gallery_position"] == 42 and restored["thumbnail_size"] == 220
