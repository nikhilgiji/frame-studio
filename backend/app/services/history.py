import json
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.extraction import Frame
from app.models.review import ActionHistory, FrameLabel
from app.schemas.history import ActionHistoryRead


class ActionHistoryService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def snapshot(self, frame_ids: list[int]) -> dict[str, object]:
        frames = list(self.session.scalars(select(Frame).where(Frame.id.in_(frame_ids))))
        labels: dict[int, list[int]] = {frame.id: [] for frame in frames}
        for frame_id, label_id in self.session.execute(
            select(FrameLabel.frame_id, FrameLabel.label_id).where(
                FrameLabel.frame_id.in_(frame_ids)
            )
        ):
            labels[frame_id].append(label_id)
        return {
            "frames": {
                str(frame.id): {
                    "labels": sorted(labels[frame.id]),
                    "review_status": frame.review_status,
                    "favorite": frame.favorite,
                    "rejected": frame.rejected,
                    "reviewed_at": frame.reviewed_at.isoformat() if frame.reviewed_at else None,
                }
                for frame in frames
            }
        }

    def record(
        self,
        project_id: int,
        action_type: str,
        description: str,
        before: dict[str, object],
        after: dict[str, object],
    ) -> ActionHistory:
        self.session.execute(
            delete(ActionHistory).where(
                ActionHistory.project_id == project_id, ActionHistory.status == "undone"
            )
        )
        action = ActionHistory(
            project_id=project_id,
            action_type=action_type,
            description=description,
            before_json=json.dumps(before),
            after_json=json.dumps(after),
        )
        self.session.add(action)
        self.session.commit()
        self.session.refresh(action)
        return action

    def list(self, project_id: int, limit: int = 100) -> list[ActionHistory]:
        return list(
            self.session.scalars(
                select(ActionHistory)
                .where(ActionHistory.project_id == project_id)
                .order_by(ActionHistory.id.desc())
                .limit(limit)
            )
        )

    def undo(self, project_id: int) -> ActionHistory:
        action = self.session.scalar(
            select(ActionHistory)
            .where(ActionHistory.project_id == project_id, ActionHistory.status == "applied")
            .order_by(ActionHistory.id.desc())
            .limit(1)
        )
        if not action:
            raise AppError("NOTHING_TO_UNDO", "There is no action to undo.", 409)
        self._restore(json.loads(action.before_json))
        action.status = "undone"
        self.session.commit()
        self.session.refresh(action)
        return action

    def redo(self, project_id: int) -> ActionHistory:
        action = self.session.scalar(
            select(ActionHistory)
            .where(ActionHistory.project_id == project_id, ActionHistory.status == "undone")
            .order_by(ActionHistory.id.asc())
            .limit(1)
        )
        if not action:
            raise AppError("NOTHING_TO_REDO", "There is no action to redo.", 409)
        self._restore(json.loads(action.after_json))
        action.status = "applied"
        self.session.commit()
        self.session.refresh(action)
        return action

    def _restore(self, snapshot: dict[str, object]) -> None:
        values = snapshot.get("frames", {})
        if not isinstance(values, dict):
            return
        ids = [int(frame_id) for frame_id in values]
        frames = {
            frame.id: frame
            for frame in self.session.scalars(select(Frame).where(Frame.id.in_(ids)))
        }
        self.session.execute(delete(FrameLabel).where(FrameLabel.frame_id.in_(ids)))
        for raw_id, raw_state in values.items():
            frame_id, state = int(raw_id), raw_state
            if frame_id not in frames or not isinstance(state, dict):
                continue
            frame = frames[frame_id]
            frame.review_status = str(state["review_status"])
            frame.favorite = bool(state["favorite"])
            frame.rejected = bool(state["rejected"])
            reviewed_at = state.get("reviewed_at")
            frame.reviewed_at = datetime.fromisoformat(str(reviewed_at)) if reviewed_at else None
            self.session.add_all(
                FrameLabel(frame_id=frame_id, label_id=int(label_id))
                for label_id in state.get("labels", [])
            )

    @staticmethod
    def serialize(action: ActionHistory) -> ActionHistoryRead:
        return ActionHistoryRead(
            id=action.id,
            project_id=action.project_id,
            action_type=action.action_type,
            description=action.description,
            status=action.status,
            created_at=action.created_at,
        )
