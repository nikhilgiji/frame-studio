from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.review import LabelRead


class FrameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    video_id: int
    video_filename: str = ""
    frame_number: int
    timestamp_seconds: float
    width: int
    height: int
    review_status: str
    favorite: bool
    rejected: bool
    reviewed_at: datetime | None
    created_at: datetime
    labels: list[LabelRead] = []


class FrameEnvelope(BaseModel):
    data: FrameRead
    error: None = None


class FramePage(BaseModel):
    items: list[FrameRead]
    page: int
    page_size: int
    total: int
    has_next: bool


class TimelineMarker(BaseModel):
    frame_id: int
    frame_number: int
    timestamp_seconds: float
    thumbnail_url: str
    labeled: bool
    rejected: bool


class VideoTimeline(BaseModel):
    video_id: int
    duration_seconds: float
    frame_count: int
    extracted_count: int
    markers: list[TimelineMarker]


class VideoTimelineEnvelope(BaseModel):
    data: VideoTimeline
    error: None = None


class FrameQuery(BaseModel):
    video_id: int | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=100, ge=1, le=500)
    review_status: str | None = None
    favorite: bool | None = None
    rejected: bool | None = None
    unlabeled: bool | None = None
    label_ids: list[int] = []
    search: str | None = None
    frame_number: int | None = None
    timestamp_min: float | None = Field(default=None, ge=0)
    timestamp_max: float | None = Field(default=None, ge=0)
    sort_by: str = "frame_number"
    sort_order: str = "asc"
