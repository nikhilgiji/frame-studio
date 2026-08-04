"""Add Phase 2 frame filtering indexes."""

from collections.abc import Sequence

from alembic import op

revision: str = "20260804_0009"
down_revision: str | None = "20260804_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_frames_project_favorite_id", "frames", ["project_id", "favorite", "id"])
    op.create_index("ix_frames_project_rejected_id", "frames", ["project_id", "rejected", "id"])
    op.create_index("ix_frames_project_review_id", "frames", ["project_id", "review_status", "id"])
    op.create_index("ix_frames_video_timestamp", "frames", ["video_id", "timestamp_seconds", "id"])
    op.create_index("ix_frames_project_reviewed_at", "frames", ["project_id", "reviewed_at"])


def downgrade() -> None:
    op.drop_index("ix_frames_project_reviewed_at", table_name="frames")
    op.drop_index("ix_frames_video_timestamp", table_name="frames")
    op.drop_index("ix_frames_project_review_id", table_name="frames")
    op.drop_index("ix_frames_project_rejected_id", table_name="frames")
    op.drop_index("ix_frames_project_favorite_id", table_name="frames")
