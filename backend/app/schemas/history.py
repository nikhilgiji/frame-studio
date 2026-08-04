from datetime import datetime

from pydantic import BaseModel


class ActionHistoryRead(BaseModel):
    id: int
    project_id: int
    action_type: str
    description: str
    status: str
    created_at: datetime


class ActionHistoryEnvelope(BaseModel):
    data: ActionHistoryRead
    error: None = None


class ActionHistoryListEnvelope(BaseModel):
    data: list[ActionHistoryRead]
    error: None = None
