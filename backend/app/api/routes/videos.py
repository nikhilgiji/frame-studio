from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.video import VideoEnvelope, VideoImportEnvelope, VideoListEnvelope, VideoRead
from app.services.video import VideoService

router = APIRouter(tags=["videos"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def service(request: Request, session: DatabaseSession) -> VideoService:
    return VideoService(session, request.app.state.settings.storage_root)


@router.post("/projects/{project_id}/videos/import", response_model=VideoImportEnvelope)
def import_videos(
    project_id: int,
    files: Annotated[list[UploadFile], File()],
    videos: Annotated[VideoService, Depends(service)],
) -> VideoImportEnvelope:
    return VideoImportEnvelope(data=videos.import_uploads(project_id, files))


@router.get("/projects/{project_id}/videos", response_model=VideoListEnvelope)
def list_videos(
    project_id: int, videos: Annotated[VideoService, Depends(service)]
) -> VideoListEnvelope:
    return VideoListEnvelope(
        data=[VideoRead.model_validate(video) for video in videos.list_for_project(project_id)]
    )


@router.get("/videos/{video_id}", response_model=VideoEnvelope)
def get_video(video_id: int, videos: Annotated[VideoService, Depends(service)]) -> VideoEnvelope:
    return VideoEnvelope(data=VideoRead.model_validate(videos.get(video_id)))


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(video_id: int, videos: Annotated[VideoService, Depends(service)]) -> Response:
    videos.delete(video_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
