"""Add persistent review queues."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260804_0007"
down_revision: str | None = "20260804_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "review_queues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("queue_type", sa.String(40), nullable=False, server_default="filtered"),
        sa.Column("filters_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("frame_ids_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_review_queues_project_updated", "review_queues", ["project_id", "updated_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_review_queues_project_updated", table_name="review_queues")
    op.drop_table("review_queues")
