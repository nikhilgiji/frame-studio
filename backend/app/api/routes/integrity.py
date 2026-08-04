from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.integrity import IntegrityCheckCreate, IntegrityReportEnvelope
from app.services.integrity import IntegrityService

router = APIRouter(tags=["integrity"])


@router.post("/projects/{project_id}/integrity-check", response_model=IntegrityReportEnvelope)
def integrity_check(
    project_id: int,
    payload: IntegrityCheckCreate,
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> IntegrityReportEnvelope:
    service = IntegrityService(session, request.app.state.settings.storage_root)
    return IntegrityReportEnvelope(data=service.scan(project_id, payload.repair_thumbnails))
