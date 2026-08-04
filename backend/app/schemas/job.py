from datetime import datetime

from pydantic import BaseModel


class UnifiedJobRead(BaseModel):
    key: str
    id: int
    project_id: int
    kind: str
    status: str
    progress: float
    error_message: str | None
    retryable: bool
    created_at: datetime
    completed_at: datetime | None


class UnifiedJobListEnvelope(BaseModel):
    data: list[UnifiedJobRead]
    error: None = None


class RetryJobEnvelope(BaseModel):
    data: UnifiedJobRead
    error: None = None


class ClearJobsResult(BaseModel):
    cleared_count: int


class ClearJobsEnvelope(BaseModel):
    data: ClearJobsResult
    error: None = None
