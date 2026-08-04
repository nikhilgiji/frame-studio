"""Add export jobs."""
from alembic import op
import sqlalchemy as sa

revision = "20260804_0006"
down_revision = "20260804_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("export_jobs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False), sa.Column("destination_path", sa.String(2048), nullable=False), sa.Column("export_mode", sa.String(32), nullable=False), sa.Column("configuration_json", sa.Text(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("progress", sa.Float(), nullable=False), sa.Column("error_message", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_export_jobs_project_status", "export_jobs", ["project_id", "status"])


def downgrade() -> None:
    op.drop_table("export_jobs")
