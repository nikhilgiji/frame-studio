from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.database.session import get_db
from app.schemas.frame import FrameEnvelope, FramePage, FrameQuery, VideoTimelineEnvelope
from app.services.frame import FrameService

router = APIRouter(tags=["frames"])


def service(request: Request, session: Annotated[Session, Depends(get_db)]) -> FrameService:
    return FrameService(session, request.app.state.settings.storage_root)


@router.get("/projects/{project_id}/frames", response_model=FramePage)
def list_frames(
    project_id: int,
    frames: Annotated[FrameService, Depends(service)],
    query: Annotated[FrameQuery, Query()],
) -> FramePage:
    return frames.list(project_id, query)


@router.get("/videos/{video_id}/timeline", response_model=VideoTimelineEnvelope)
def video_timeline(
    video_id: int,
    frames: Annotated[FrameService, Depends(service)],
    marker_limit: Annotated[int, Query(ge=3, le=300)] = 120,
) -> VideoTimelineEnvelope:
    return VideoTimelineEnvelope(data=frames.timeline(video_id, marker_limit))


@router.get("/videos/{video_id}/frames/nearest", response_model=FrameEnvelope)
def nearest_frame(
    video_id: int,
    frames: Annotated[FrameService, Depends(service)],
    timestamp: Annotated[float | None, Query(ge=0)] = None,
    frame_number: Annotated[int | None, Query(ge=0)] = None,
) -> FrameEnvelope:
    if timestamp is None and frame_number is None:
        raise AppError("NAVIGATION_TARGET_REQUIRED", "Provide a timestamp or frame number.", 422)
    return FrameEnvelope(data=frames.nearest(video_id, timestamp, frame_number))


@router.get("/frames/{frame_id}", response_model=FrameEnvelope)
def get_frame(frame_id: int, frames: Annotated[FrameService, Depends(service)]) -> FrameEnvelope:
    return FrameEnvelope(data=frames.serialize(frames.get(frame_id)))


@router.get("/frames/{frame_id}/thumbnail")
def thumbnail(frame_id: int, frames: Annotated[FrameService, Depends(service)]) -> FileResponse:
    return FileResponse(frames.thumbnail(frame_id), media_type="image/jpeg")


@router.get("/frames/{frame_id}/image")
def image(frame_id: int, frames: Annotated[FrameService, Depends(service)]) -> FileResponse:
    return FileResponse(frames.image(frame_id))
