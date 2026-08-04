from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.queue import (
    ReviewQueueCreate,
    ReviewQueueEnvelope,
    ReviewQueueListEnvelope,
    ReviewQueueUpdate,
)
from app.services.queue import ReviewQueueService

router = APIRouter(tags=["review queues"])


def service(request: Request, session: Annotated[Session, Depends(get_db)]) -> ReviewQueueService:
    return ReviewQueueService(session, request.app.state.settings.storage_root)


@router.post(
    "/projects/{project_id}/review-queues",
    response_model=ReviewQueueEnvelope,
    status_code=201,
)
def create_queue(
    project_id: int,
    payload: ReviewQueueCreate,
    queues: Annotated[ReviewQueueService, Depends(service)],
) -> ReviewQueueEnvelope:
    return ReviewQueueEnvelope(data=queues.serialize(queues.create(project_id, payload)))


@router.get("/projects/{project_id}/review-queues", response_model=ReviewQueueListEnvelope)
def list_queues(
    project_id: int, queues: Annotated[ReviewQueueService, Depends(service)]
) -> ReviewQueueListEnvelope:
    return ReviewQueueListEnvelope(
        data=[queues.serialize(queue) for queue in queues.list(project_id)]
    )


@router.get("/review-queues/{queue_id}", response_model=ReviewQueueEnvelope)
def get_queue(
    queue_id: int, queues: Annotated[ReviewQueueService, Depends(service)]
) -> ReviewQueueEnvelope:
    return ReviewQueueEnvelope(data=queues.serialize(queues.get(queue_id)))


@router.patch("/review-queues/{queue_id}", response_model=ReviewQueueEnvelope)
def update_queue(
    queue_id: int,
    payload: ReviewQueueUpdate,
    queues: Annotated[ReviewQueueService, Depends(service)],
) -> ReviewQueueEnvelope:
    return ReviewQueueEnvelope(data=queues.serialize(queues.update(queue_id, payload.position)))


@router.delete("/review-queues/{queue_id}", status_code=204)
def delete_queue(
    queue_id: int, queues: Annotated[ReviewQueueService, Depends(service)]
) -> Response:
    queues.delete(queue_id)
    return Response(status_code=204)
