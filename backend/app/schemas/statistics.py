from datetime import date

from pydantic import BaseModel


class NamedCount(BaseModel):
    id: int
    name: str
    count: int


class DatedCount(BaseModel):
    date: date
    count: int


class ProjectStatistics(BaseModel):
    total_projects: int
    total_videos: int
    total_frames: int
    reviewed_frames: int
    unreviewed_frames: int
    rejected_frames: int
    favorite_frames: int
    extraction_jobs: int
    export_jobs: int
    frames_per_label: list[NamedCount]
    frames_per_video: list[NamedCount]
    review_progress: list[DatedCount]


class ProjectStatisticsEnvelope(BaseModel):
    data: ProjectStatistics
    error: None = None
