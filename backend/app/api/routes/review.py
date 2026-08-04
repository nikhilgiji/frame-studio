from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.frame import FrameEnvelope
from app.schemas.review import (
    BulkActionEnvelope,
    BulkActionResult,
    BulkLabelUpdate,
    BulkReviewUpdate,
    FilteredLabelUpdate,
    FilteredReviewUpdate,
    FrameLabelsUpdate,
    LabelCreate,
    LabelEnvelope,
    LabelListEnvelope,
    LabelRead,
    LabelUpdate,
    ReviewSessionEnvelope,
    ReviewSessionUpdate,
    ReviewUpdate,
)
from app.services.frame import FrameService
from app.services.project import ProjectService
from app.services.review import LabelService, ReviewService, ReviewSessionService

router = APIRouter(tags=["review"])


def db(session: Annotated[Session, Depends(get_db)]) -> Session:
    return session


@router.get("/projects/{project_id}/labels", response_model=LabelListEnvelope)
def labels(project_id: int, session: Annotated[Session, Depends(db)]) -> LabelListEnvelope:
    return LabelListEnvelope(
        data=[LabelRead.model_validate(label) for label in LabelService(session).list(project_id)]
    )


@router.post("/projects/{project_id}/labels", response_model=LabelEnvelope, status_code=201)
def create_label(
    project_id: int,
    payload: LabelCreate,
    request: Request,
    session: Annotated[Session, Depends(db)],
) -> LabelEnvelope:
    ProjectService(session, request.app.state.settings.storage_root).get(project_id)
    return LabelEnvelope(
        data=LabelRead.model_validate(LabelService(session).create(project_id, payload))
    )


@router.patch("/labels/{label_id}", response_model=LabelEnvelope)
def update_label(
    label_id: int, payload: LabelUpdate, session: Annotated[Session, Depends(db)]
) -> LabelEnvelope:
    return LabelEnvelope(
        data=LabelRead.model_validate(LabelService(session).update(label_id, payload))
    )


@router.delete("/labels/{label_id}", status_code=204)
def delete_label(label_id: int, session: Annotated[Session, Depends(db)]) -> Response:
    LabelService(session).delete(label_id)
    return Response(status_code=204)


def frame_envelope(frame_id: int, request: Request, session: Session) -> FrameEnvelope:
    frames = FrameService(session, request.app.state.settings.storage_root)
    return FrameEnvelope(data=frames.serialize(frames.get(frame_id)))


@router.post("/frames/{frame_id}/labels", response_model=FrameEnvelope)
def assign_labels(
    frame_id: int,
    payload: FrameLabelsUpdate,
    request: Request,
    session: Annotated[Session, Depends(db)],
) -> FrameEnvelope:
    ReviewService(session).labels(frame_id, payload.label_ids)
    return frame_envelope(frame_id, request, session)


@router.delete("/frames/{frame_id}/labels/{label_id}", response_model=FrameEnvelope)
def remove_label(
    frame_id: int, label_id: int, request: Request, session: Annotated[Session, Depends(db)]
) -> FrameEnvelope:
    ReviewService(session).remove_label(frame_id, label_id)
    return frame_envelope(frame_id, request, session)


@router.post("/frames/bulk-label", status_code=204)
def bulk_label(payload: BulkLabelUpdate, session: Annotated[Session, Depends(db)]) -> Response:
    ReviewService(session).bulk_labels(payload.frame_ids, payload.label_ids, payload.action)
    return Response(status_code=204)


@router.patch("/frames/{frame_id}/review", response_model=FrameEnvelope)
def review_frame(
    frame_id: int, payload: ReviewUpdate, request: Request, session: Annotated[Session, Depends(db)]
) -> FrameEnvelope:
    ReviewService(session).review(frame_id, payload)
    return frame_envelope(frame_id, request, session)


@router.post("/frames/bulk-review", status_code=204)
def bulk_review(payload: BulkReviewUpdate, session: Annotated[Session, Depends(db)]) -> Response:
    ReviewService(session).bulk_review(
        payload.frame_ids, ReviewUpdate(**payload.model_dump(exclude={"frame_ids"}))
    )
    return Response(status_code=204)


@router.post("/projects/{project_id}/frames/bulk-label", response_model=BulkActionEnvelope)
def filtered_bulk_label(
    project_id: int,
    payload: FilteredLabelUpdate,
    request: Request,
    session: Annotated[Session, Depends(db)],
) -> BulkActionEnvelope:
    service = ReviewService(session)
    ids = service.resolve_target(
        project_id,
        payload.frame_ids,
        payload.all_filtered,
        payload.filters,
        request.app.state.settings.storage_root,
    )
    service.bulk_labels(ids, payload.label_ids, payload.action)
    return BulkActionEnvelope(data=BulkActionResult(affected_count=len(ids)))


@router.post("/projects/{project_id}/frames/bulk-review", response_model=BulkActionEnvelope)
def filtered_bulk_review(
    project_id: int,
    payload: FilteredReviewUpdate,
    request: Request,
    session: Annotated[Session, Depends(db)],
) -> BulkActionEnvelope:
    service = ReviewService(session)
    ids = service.resolve_target(
        project_id,
        payload.frame_ids,
        payload.all_filtered,
        payload.filters,
        request.app.state.settings.storage_root,
    )
    service.bulk_review(
        ids,
        ReviewUpdate(**payload.model_dump(exclude={"frame_ids", "all_filtered", "filters"})),
    )
    return BulkActionEnvelope(data=BulkActionResult(affected_count=len(ids)))


@router.get("/projects/{project_id}/review-session", response_model=ReviewSessionEnvelope)
def get_review_session(
    project_id: int, session: Annotated[Session, Depends(db)]
) -> ReviewSessionEnvelope:
    service = ReviewSessionService(session)
    return ReviewSessionEnvelope(data=service.serialize(service.get(project_id)))


@router.patch("/projects/{project_id}/review-session", response_model=ReviewSessionEnvelope)
def update_review_session(
    project_id: int, payload: ReviewSessionUpdate, session: Annotated[Session, Depends(db)]
) -> ReviewSessionEnvelope:
    service = ReviewSessionService(session)
    return ReviewSessionEnvelope(data=service.serialize(service.update(project_id, payload)))
