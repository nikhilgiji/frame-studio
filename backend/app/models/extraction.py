from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"
    __table_args__ = (Index("ix_extraction_jobs_project_status", "project_id", "status"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    mode_value: Mapped[float] = mapped_column(Float, nullable=False)
    output_format: Mapped[str] = mapped_column(String(8), nullable=False)
    jpeg_quality: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    resize_width: Mapped[int | None] = mapped_column(Integer)
    resize_height: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    processed_frames: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_frames: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Frame(Base):
    __tablename__ = "frames"
    __table_args__ = (
        Index("ix_frames_project_video_number", "project_id", "video_id", "frame_number"),
        Index("ix_frames_project_favorite_id", "project_id", "favorite", "id"),
        Index("ix_frames_project_rejected_id", "project_id", "rejected", "id"),
        Index("ix_frames_project_review_id", "project_id", "review_status", "id"),
        Index("ix_frames_video_timestamp", "video_id", "timestamp_seconds", "id"),
        Index("ix_frames_project_reviewed_at", "project_id", "reviewed_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    image_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    thumbnail_path: Mapped[str | None] = mapped_column(String(2048))
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    review_status: Mapped[str] = mapped_column(String(24), nullable=False, default="unreviewed")
    favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rejected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
