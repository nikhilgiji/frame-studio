from pydantic import BaseModel


class IntegrityCheckCreate(BaseModel):
    repair_thumbnails: bool = True


class IntegrityIssue(BaseModel):
    code: str
    message: str
    path: str | None = None
    entity_type: str
    entity_id: int
    repairable: bool
    repaired: bool = False


class IntegrityReport(BaseModel):
    project_id: int
    checked_videos: int
    checked_frames: int
    issue_count: int
    repaired_count: int
    issues: list[IntegrityIssue]


class IntegrityReportEnvelope(BaseModel):
    data: IntegrityReport
    error: None = None
