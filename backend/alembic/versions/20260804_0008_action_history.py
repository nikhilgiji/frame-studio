"""Add persisted action history."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260804_0008"
down_revision: str | None = "20260804_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "action_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(40), nullable=False),
        sa.Column("description", sa.String(300), nullable=False),
        sa.Column("before_json", sa.Text(), nullable=False),
        sa.Column("after_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="applied"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_action_history_project_created", "action_history", ["project_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_action_history_project_created", table_name="action_history")
    op.drop_table("action_history")
