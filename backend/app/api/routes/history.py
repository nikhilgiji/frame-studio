from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.history import ActionHistoryEnvelope, ActionHistoryListEnvelope
from app.services.history import ActionHistoryService

router = APIRouter(tags=["action history"])


@router.get("/projects/{project_id}/action-history", response_model=ActionHistoryListEnvelope)
def history(
    project_id: int,
    session: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> ActionHistoryListEnvelope:
    service = ActionHistoryService(session)
    return ActionHistoryListEnvelope(
        data=[service.serialize(action) for action in service.list(project_id, limit)]
    )


@router.post("/projects/{project_id}/action-history/undo", response_model=ActionHistoryEnvelope)
def undo(project_id: int, session: Annotated[Session, Depends(get_db)]) -> ActionHistoryEnvelope:
    service = ActionHistoryService(session)
    return ActionHistoryEnvelope(data=service.serialize(service.undo(project_id)))


@router.post("/projects/{project_id}/action-history/redo", response_model=ActionHistoryEnvelope)
def redo(project_id: int, session: Annotated[Session, Depends(get_db)]) -> ActionHistoryEnvelope:
    service = ActionHistoryService(session)
    return ActionHistoryEnvelope(data=service.serialize(service.redo(project_id)))
