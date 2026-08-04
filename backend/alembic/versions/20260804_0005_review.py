"""Add labels and review sessions."""

import sqlalchemy as sa

from alembic import op

revision = "20260804_0005"
down_revision = "20260804_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "labels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_key", sa.String(100), nullable=False),
        sa.Column("shortcut", sa.String(16)),
        sa.Column("shortcut_key", sa.String(16)),
        sa.Column("color", sa.String(16), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("project_id", "name_key", name="uq_labels_project_name"),
        sa.UniqueConstraint("project_id", "shortcut_key", name="uq_labels_project_shortcut"),
    )
    op.create_index("ix_labels_project_position", "labels", ["project_id", "position"])
    op.create_table(
        "frame_labels",
        sa.Column(
            "frame_id",
            sa.Integer(),
            sa.ForeignKey("frames.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "label_id",
            sa.Integer(),
            sa.ForeignKey("labels.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "review_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("video_id", sa.Integer(), sa.ForeignKey("videos.id", ondelete="SET NULL")),
        sa.Column("last_frame_id", sa.Integer(), sa.ForeignKey("frames.id", ondelete="SET NULL")),
        sa.Column("active_filters_json", sa.Text(), nullable=False),
        sa.Column("gallery_position", sa.Integer(), nullable=False),
        sa.Column("thumbnail_size", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("project_id", name="uq_review_sessions_project"),
    )


def downgrade() -> None:
    op.drop_table("review_sessions")
    op.drop_table("frame_labels")
    op.drop_table("labels")
