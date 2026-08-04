from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LabelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    shortcut: str | None = Field(default=None, max_length=16)
    color: str = Field(default="#69e2bc", pattern=r"^#[0-9a-fA-F]{6}$")
    description: str = Field(default="", max_length=1000)
    position: int | None = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Label name cannot be blank.")
        return value

    @field_validator("shortcut")
    @classmethod
    def clean_shortcut(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class LabelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    shortcut: str | None = Field(default=None, max_length=16)
    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    description: str | None = Field(default=None, max_length=1000)
    position: int | None = Field(default=None, ge=0)


class LabelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    name: str
    shortcut: str | None
    color: str
    description: str
    position: int
    created_at: datetime


class LabelEnvelope(BaseModel):
    data: LabelRead
    error: None = None


class LabelListEnvelope(BaseModel):
    data: list[LabelRead]
    error: None = None


class FrameLabelsUpdate(BaseModel):
    label_ids: list[int]


class BulkLabelUpdate(FrameLabelsUpdate):
    frame_ids: list[int] = Field(min_length=1, max_length=10000)
    action: str = "assign"


class ReviewUpdate(BaseModel):
    review_status: str | None = None
    favorite: bool | None = None
    rejected: bool | None = None


class BulkReviewUpdate(ReviewUpdate):
    frame_ids: list[int] = Field(min_length=1, max_length=10000)


class FilteredTarget(BaseModel):
    frame_ids: list[int] = Field(default=[], max_length=10000)
    all_filtered: bool = False
    filters: dict[str, object] = {}


class FilteredLabelUpdate(FilteredTarget):
    label_ids: list[int] = Field(min_length=1, max_length=1000)
    action: str = "assign"


class FilteredReviewUpdate(FilteredTarget, ReviewUpdate):
    pass


class BulkActionResult(BaseModel):
    affected_count: int


class BulkActionEnvelope(BaseModel):
    data: BulkActionResult
    error: None = None


class ReviewSessionUpdate(BaseModel):
    video_id: int | None = None
    last_frame_id: int | None = None
    active_filters: dict[str, object] | None = None
    gallery_position: int | None = Field(default=None, ge=0)
    thumbnail_size: int | None = Field(default=None, ge=80, le=400)


class ReviewSessionRead(BaseModel):
    id: int
    project_id: int
    video_id: int | None
    last_frame_id: int | None
    active_filters: dict[str, object]
    gallery_position: int
    thumbnail_size: int
    created_at: datetime
    updated_at: datetime


class ReviewSessionEnvelope(BaseModel):
    data: ReviewSessionRead
    error: None = None
