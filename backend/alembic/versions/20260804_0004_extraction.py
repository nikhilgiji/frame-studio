"""Add extraction jobs and frames."""

import sqlalchemy as sa

from alembic import op

revision = "20260804_0004"
down_revision = "20260804_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "extraction_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "video_id", sa.Integer(), sa.ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("mode_value", sa.Float(), nullable=False),
        sa.Column("output_format", sa.String(8), nullable=False),
        sa.Column("jpeg_quality", sa.Integer(), nullable=False),
        sa.Column("resize_width", sa.Integer()),
        sa.Column("resize_height", sa.Integer()),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("progress", sa.Float(), nullable=False),
        sa.Column("processed_frames", sa.Integer(), nullable=False),
        sa.Column("total_frames", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_extraction_jobs_project_status", "extraction_jobs", ["project_id", "status"]
    )
    op.create_table(
        "frames",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "video_id", sa.Integer(), sa.ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("frame_number", sa.Integer(), nullable=False),
        sa.Column("timestamp_seconds", sa.Float(), nullable=False),
        sa.Column("image_path", sa.String(2048), nullable=False),
        sa.Column("thumbnail_path", sa.String(2048)),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("review_status", sa.String(24), nullable=False, server_default="unreviewed"),
        sa.Column("favorite", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("rejected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_frames_project_video_number", "frames", ["project_id", "video_id", "frame_number"]
    )


def downgrade() -> None:
    op.drop_table("frames")
    op.drop_table("extraction_jobs")
