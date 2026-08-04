"""Add unified maintenance jobs."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260804_0010"
down_revision: str | None = "20260804_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "maintenance_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("configuration_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_maintenance_jobs_project_status",
        "maintenance_jobs",
        ["project_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_maintenance_jobs_project_status", table_name="maintenance_jobs")
    op.drop_table("maintenance_jobs")
