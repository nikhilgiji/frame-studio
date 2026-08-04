from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.statistics import ProjectStatisticsEnvelope
from app.services.statistics import StatisticsService

router = APIRouter(tags=["statistics"])


@router.get("/projects/{project_id}/statistics", response_model=ProjectStatisticsEnvelope)
def statistics(
    project_id: int,
    session: Annotated[Session, Depends(get_db)],
    video_id: int | None = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> ProjectStatisticsEnvelope:
    return ProjectStatisticsEnvelope(
        data=StatisticsService(session).project(project_id, video_id, date_from, date_to)
    )
