from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VideoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    filename: str
    source_path: str
    stored_path: str
    file_size: int
    fps: float
    duration_seconds: float
    frame_count: int
    width: int
    height: int
    codec: str
    status: str
    created_at: datetime


class ImportIssue(BaseModel):
    filename: str
    code: str
    message: str


class VideoImportData(BaseModel):
    imported: list[VideoRead]
    skipped: list[ImportIssue]
    errors: list[ImportIssue]


class VideoImportEnvelope(BaseModel):
    data: VideoImportData
    error: None = None


class VideoEnvelope(BaseModel):
    data: VideoRead
    error: None = None


class VideoListEnvelope(BaseModel):
    data: list[VideoRead]
    error: None = None
