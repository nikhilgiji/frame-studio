from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint("project_id", "name_key", name="uq_labels_project_name"),
        UniqueConstraint("project_id", "shortcut_key", name="uq_labels_project_shortcut"),
        Index("ix_labels_project_position", "project_id", "position"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_key: Mapped[str] = mapped_column(String(100), nullable=False)
    shortcut: Mapped[str | None] = mapped_column(String(16))
    shortcut_key: Mapped[str | None] = mapped_column(String(16))
    color: Mapped[str] = mapped_column(String(16), nullable=False, default="#69e2bc")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FrameLabel(Base):
    __tablename__ = "frame_labels"
    frame_id: Mapped[int] = mapped_column(
        ForeignKey("frames.id", ondelete="CASCADE"), primary_key=True
    )
    label_id: Mapped[int] = mapped_column(
        ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReviewSession(Base):
    __tablename__ = "review_sessions"
    __table_args__ = (UniqueConstraint("project_id", name="uq_review_sessions_project"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    video_id: Mapped[int | None] = mapped_column(ForeignKey("videos.id", ondelete="SET NULL"))
    last_frame_id: Mapped[int | None] = mapped_column(ForeignKey("frames.id", ondelete="SET NULL"))
    active_filters_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    gallery_position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    thumbnail_size: Mapped[int] = mapped_column(Integer, nullable=False, default=180)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
