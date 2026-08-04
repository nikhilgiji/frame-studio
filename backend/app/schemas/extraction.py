from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExtractionCreate(BaseModel):
    mode: Literal["every_n_frames", "frames_per_second", "every_n_seconds"]
    mode_value: float = Field(gt=0)
    output_format: Literal["jpeg", "png"] = "jpeg"
    jpeg_quality: int = Field(default=90, ge=1, le=100)
    resize_width: int | None = Field(default=None, gt=0)
    resize_height: int | None = Field(default=None, gt=0)
    overwrite: bool = False

    @model_validator(mode="after")
    def validate_mode(self) -> "ExtractionCreate":
        if self.mode == "every_n_frames" and not self.mode_value.is_integer():
            raise ValueError("Every-N-frames must be a whole number.")
        return self


class ExtractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    video_id: int
    mode: str
    mode_value: float
    output_format: str
    jpeg_quality: int
    resize_width: int | None
    resize_height: int | None
    status: str
    progress: float
    processed_frames: int
    total_frames: int
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class ExtractionEnvelope(BaseModel):
    data: ExtractionRead
    error: None = None


class ExtractionListEnvelope(BaseModel):
    data: list[ExtractionRead]
    error: None = None
