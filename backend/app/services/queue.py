import json
import random
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.extraction import Frame
from app.models.review import ReviewQueue
from app.schemas.queue import ReviewQueueCreate, ReviewQueueRead
from app.services.frame import FrameService


class ReviewQueueService:
    def __init__(self, session: Session, storage_root: Path) -> None:
        self.session = session
        self.frames = FrameService(session, storage_root)

    def create(self, project_id: int, payload: ReviewQueueCreate) -> ReviewQueue:
        filters = dict(payload.filters)
        presets: dict[str, dict[str, object]] = {
            "unreviewed": {"review_status": "unreviewed"},
            "rejected": {"rejected": True},
            "favorites": {"favorite": True},
        }
        filters.update(presets.get(payload.queue_type, {}))
        ids = list(self.frames.matching_ids(project_id, filters))
        if payload.queue_type == "random":
            random.Random(0).shuffle(ids)
            ids = ids[: payload.random_limit or min(100, len(ids))]
        queue = ReviewQueue(
            project_id=project_id,
            name=payload.name.strip(),
            queue_type=payload.queue_type,
            filters_json=json.dumps(filters),
            frame_ids_json=json.dumps(ids),
        )
        self.session.add(queue)
        self.session.commit()
        self.session.refresh(queue)
        return queue

    def list(self, project_id: int) -> list[ReviewQueue]:
        self.frames.projects.get(project_id)
        return list(
            self.session.scalars(
                select(ReviewQueue)
                .where(ReviewQueue.project_id == project_id)
                .order_by(ReviewQueue.updated_at.desc(), ReviewQueue.id.desc())
            )
        )

    def get(self, queue_id: int) -> ReviewQueue:
        queue = self.session.get(ReviewQueue, queue_id)
        if not queue:
            raise AppError("REVIEW_QUEUE_NOT_FOUND", "The review queue does not exist.", 404)
        return queue

    def update(self, queue_id: int, position: int) -> ReviewQueue:
        queue = self.get(queue_id)
        ids: list[int] = json.loads(queue.frame_ids_json)
        queue.position = min(position, max(0, len(ids) - 1))
        self.session.commit()
        self.session.refresh(queue)
        return queue

    def delete(self, queue_id: int) -> None:
        self.session.delete(self.get(queue_id))
        self.session.commit()

    def serialize(self, queue: ReviewQueue) -> ReviewQueueRead:
        ids: list[int] = json.loads(queue.frame_ids_json)
        reviewed = 0
        if ids:
            reviewed = (
                self.session.scalar(
                    select(func.count(Frame.id)).where(
                        Frame.id.in_(ids), Frame.review_status == "reviewed"
                    )
                )
                or 0
            )
        position = min(queue.position, max(0, len(ids) - 1))
        return ReviewQueueRead(
            id=queue.id,
            project_id=queue.project_id,
            name=queue.name,
            queue_type=queue.queue_type,
            filters=json.loads(queue.filters_json),
            position=position,
            current_frame_id=ids[position] if ids else None,
            total=len(ids),
            reviewed=reviewed,
            remaining=max(0, len(ids) - reviewed),
            completion_percentage=(reviewed / len(ids) * 100) if ids else 100,
            created_at=queue.created_at,
            updated_at=queue.updated_at,
        )
