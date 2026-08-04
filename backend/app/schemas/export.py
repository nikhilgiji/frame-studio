from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExportCreate(BaseModel):
    destination_name: str = Field(default="dataset", pattern=r"^[A-Za-z0-9._ -]+$", max_length=100)
    export_mode: Literal["label_folders", "selected", "favorites", "reviewed", "manifest"]
    frame_ids: list[int] = Field(default=[], max_length=100000)
    label_ids: list[int] = Field(default=[], max_length=1000)
    multi_label_mode: Literal["copy_each", "manifest_only"] = "copy_each"
    conflict: Literal["skip", "overwrite", "rename"] = "rename"


class ExportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    destination_path: str
    export_mode: str
    status: str
    progress: float
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None


class ExportEnvelope(BaseModel):
    data: ExportRead
    error: None = None
