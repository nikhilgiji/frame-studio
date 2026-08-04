"""Add projects.

Revision ID: 20260804_0002
Revises: 20260804_0001
Create Date: 2026-08-04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260804_0002"
down_revision = "20260804_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("root_path", sa.String(length=1024), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("root_path"),
    )
    op.create_index("uq_projects_name_ci", "projects", [sa.text("lower(name)")], unique=True)


def downgrade() -> None:
    op.drop_index("uq_projects_name_ci", table_name="projects")
    op.drop_table("projects")
