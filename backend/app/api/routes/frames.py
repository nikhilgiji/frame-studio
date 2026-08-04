from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.frame import FrameEnvelope, FramePage, FrameQuery
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


@router.get("/frames/{frame_id}", response_model=FrameEnvelope)
def get_frame(frame_id: int, frames: Annotated[FrameService, Depends(service)]) -> FrameEnvelope:
    return FrameEnvelope(data=frames.serialize(frames.get(frame_id)))


@router.get("/frames/{frame_id}/thumbnail")
def thumbnail(frame_id: int, frames: Annotated[FrameService, Depends(service)]) -> FileResponse:
    return FileResponse(frames.thumbnail(frame_id), media_type="image/jpeg")


@router.get("/frames/{frame_id}/image")
def image(frame_id: int, frames: Annotated[FrameService, Depends(service)]) -> FileResponse:
    return FileResponse(frames.image(frame_id))
