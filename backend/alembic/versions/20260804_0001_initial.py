"""Initialize the Vision Curator database.

Revision ID: 20260804_0001
Revises:
Create Date: 2026-08-04
"""

revision = "20260804_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Reserve the initial schema revision; domain tables begin in Phase 1.2."""


def downgrade() -> None:
    """Return to an unversioned database."""
