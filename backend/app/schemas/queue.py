from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ReviewQueueCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    queue_type: Literal[
        "unreviewed", "video", "label", "rejected", "favorites", "random", "filtered"
    ] = "filtered"
    filters: dict[str, object] = {}
    random_limit: int | None = Field(default=None, ge=1, le=100000)


class ReviewQueueUpdate(BaseModel):
    position: int = Field(ge=0)


class ReviewQueueRead(BaseModel):
    id: int
    project_id: int
    name: str
    queue_type: str
    filters: dict[str, object]
    position: int
    current_frame_id: int | None
    total: int
    reviewed: int
    remaining: int
    completion_percentage: float
    created_at: datetime
    updated_at: datetime


class ReviewQueueEnvelope(BaseModel):
    data: ReviewQueueRead
    error: None = None


class ReviewQueueListEnvelope(BaseModel):
    data: list[ReviewQueueRead]
    error: None = None
