"""Add videos.

Revision ID: 20260804_0003
Revises: 20260804_0002
Create Date: 2026-08-04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260804_0003"
down_revision = "20260804_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "videos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("source_path", sa.String(2048), nullable=False),
        sa.Column("stored_path", sa.String(2048), nullable=False, unique=True),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("fps", sa.Float(), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
        sa.Column("frame_count", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("codec", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ready"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "content_hash", name="uq_videos_project_hash"),
    )
    op.create_index("ix_videos_project_status", "videos", ["project_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_videos_project_status", table_name="videos")
    op.drop_table("videos")
