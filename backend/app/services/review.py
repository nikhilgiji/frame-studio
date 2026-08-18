import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.extraction import Frame
from app.models.review import FrameLabel, Label, ReviewSession
from app.schemas.review import (
    LabelCreate,
    LabelUpdate,
    ReviewSessionRead,
    ReviewSessionUpdate,
    ReviewUpdate,
)
from app.services.history import ActionHistoryService


class LabelService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, project_id: int) -> list[Label]:
        return list(
            self.session.scalars(
                select(Label)
                .where(Label.project_id == project_id)
                .order_by(Label.position, Label.id)
            )
        )

    def get(self, label_id: int) -> Label:
        label = self.session.get(Label, label_id)
        if not label:
            raise AppError("LABEL_NOT_FOUND", "The requested label does not exist.", 404)
        return label

    def create(self, project_id: int, payload: LabelCreate) -> Label:
        position = payload.position
        if position is None:
            position = int(
                self.session.scalar(
                    select(func.count(Label.id)).where(Label.project_id == project_id)
                )
                or 0
            )
        label = Label(
            project_id=project_id,
            name=payload.name,
            name_key=payload.name.casefold(),
            shortcut=payload.shortcut,
            shortcut_key=payload.shortcut.casefold() if payload.shortcut else None,
            color=payload.color,
            description=payload.description,
            position=position,
        )
        return self._save(label)

    def update(self, label_id: int, payload: LabelUpdate) -> Label:
        label = self.get(label_id)
        updates = payload.model_dump(exclude_unset=True)
        new_position = updates.get("position")
        if new_position is not None and new_position != label.position:
            target = self.session.scalar(
                select(Label).where(
                    Label.project_id == label.project_id,
                    Label.position == new_position,
                    Label.id != label.id,
                )
            )
            if target:
                target.position = label.position
        for key, value in updates.items():
            setattr(label, key, value)
        if "name" in updates:
            label.name_key = label.name.casefold()
        if "shortcut" in updates:
            label.shortcut_key = label.shortcut.casefold() if label.shortcut else None
        return self._save(label)

    def delete(self, label_id: int) -> None:
        label = self.get(label_id)
        self.session.execute(delete(FrameLabel).where(FrameLabel.label_id == label_id))
        self.session.delete(label)
        self.session.commit()

    def _save(self, label: Label) -> Label:
        self.session.add(label)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise AppError(
                "LABEL_CONFLICT", "A label name or keyboard shortcut is already in use.", 409
            ) from exc
        self.session.refresh(label)
        return label


class ReviewService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def labels(self, frame_id: int, label_ids: list[int]) -> Frame:
        frame = self._frame(frame_id)
        history = ActionHistoryService(self.session)
        before = history.snapshot([frame_id])
        valid = self._valid_labels(frame.project_id, label_ids)
        for label_id in valid:
            if not self.session.get(FrameLabel, (frame_id, label_id)):
                self.session.add(FrameLabel(frame_id=frame_id, label_id=label_id))
        self.session.commit()
        names = list(self.session.scalars(select(Label.name).where(Label.id.in_(valid))))
        history.record(
            frame.project_id,
            "label_assignment",
            f"Assigned {', '.join(names)} to 1 frame",
            before,
            history.snapshot([frame_id]),
        )
        return frame

    def remove_label(self, frame_id: int, label_id: int) -> Frame:
        frame = self._frame(frame_id)
        history = ActionHistoryService(self.session)
        before = history.snapshot([frame_id])
        label = self.session.get(Label, label_id)
        self.session.execute(
            delete(FrameLabel).where(
                FrameLabel.frame_id == frame_id, FrameLabel.label_id == label_id
            )
        )
        self.session.commit()
        history.record(
            frame.project_id,
            "label_removal",
            f'Removed "{label.name if label else label_id}" from 1 frame',
            before,
            history.snapshot([frame_id]),
        )
        return frame

    def bulk_labels(self, frame_ids: list[int], label_ids: list[int], action: str) -> None:
        frames = list(self.session.scalars(select(Frame).where(Frame.id.in_(frame_ids))))
        if len(frames) != len(set(frame_ids)):
            raise AppError("FRAME_NOT_FOUND", "One or more frames do not exist.", 404)
        project_ids = {frame.project_id for frame in frames}
        if len(project_ids) != 1:
            raise AppError("PROJECT_MISMATCH", "Bulk actions must remain within one project.", 409)
        valid = self._valid_labels(next(iter(project_ids)), label_ids)
        history = ActionHistoryService(self.session)
        before = history.snapshot(frame_ids)
        if action == "remove":
            self.session.execute(
                delete(FrameLabel).where(
                    FrameLabel.frame_id.in_(frame_ids), FrameLabel.label_id.in_(valid)
                )
            )
        else:
            existing = set(
                self.session.execute(
                    select(FrameLabel.frame_id, FrameLabel.label_id).where(
                        FrameLabel.frame_id.in_(frame_ids), FrameLabel.label_id.in_(valid)
                    )
                ).all()
            )
            self.session.add_all(
                FrameLabel(frame_id=frame_id, label_id=label_id)
                for frame_id in frame_ids
                for label_id in valid
                if (frame_id, label_id) not in existing
            )
        self.session.commit()
        names = list(self.session.scalars(select(Label.name).where(Label.id.in_(valid))))
        verb = "Removed" if action == "remove" else "Assigned"
        direction = "from" if action == "remove" else "to"
        history.record(
            next(iter(project_ids)),
            f"label_{action}",
            f"{verb} {', '.join(names)} {direction} {len(frame_ids)} frames",
            before,
            history.snapshot(frame_ids),
        )

    def review(self, frame_id: int, payload: ReviewUpdate) -> Frame:
        frame = self._frame(frame_id)
        history = ActionHistoryService(self.session)
        before = history.snapshot([frame_id])
        self._apply_review(frame, payload)
        self.session.commit()
        self.session.refresh(frame)
        history.record(
            frame.project_id,
            "review_change",
            "Updated review state for 1 frame",
            before,
            history.snapshot([frame_id]),
        )
        return frame

    def bulk_review(self, frame_ids: list[int], payload: ReviewUpdate) -> None:
        frames = list(self.session.scalars(select(Frame).where(Frame.id.in_(frame_ids))))
        if not frames:
            raise AppError("EMPTY_SELECTION", "No frames match this batch action.", 409)
        history = ActionHistoryService(self.session)
        before = history.snapshot(frame_ids)
        for frame in frames:
            self._apply_review(frame, payload)
        self.session.commit()
        history.record(
            frames[0].project_id,
            "bulk_review",
            f"Updated review state for {len(frames)} frames",
            before,
            history.snapshot(frame_ids),
        )

    def resolve_target(
        self,
        project_id: int,
        frame_ids: list[int],
        all_filtered: bool,
        filters: dict[str, object],
        storage_root: Path,
    ) -> list[int]:
        if all_filtered:
            from app.services.frame import FrameService

            ids = FrameService(self.session, storage_root).matching_ids(project_id, filters)
        else:
            ids = frame_ids
        if not ids:
            raise AppError("EMPTY_SELECTION", "No frames match this batch action.", 409)
        count = self.session.scalar(
            select(func.count(Frame.id)).where(Frame.project_id == project_id, Frame.id.in_(ids))
        )
        if count != len(set(ids)):
            raise AppError("PROJECT_MISMATCH", "The selection contains invalid frames.", 409)
        return list(dict.fromkeys(ids))

    def _apply_review(self, frame: Frame, payload: ReviewUpdate) -> None:
        for key, value in payload.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(frame, key, value)
        if payload.review_status == "reviewed":
            frame.reviewed_at = datetime.now(UTC)
        elif payload.review_status == "unreviewed":
            frame.reviewed_at = None

    def _frame(self, frame_id: int) -> Frame:
        frame = self.session.get(Frame, frame_id)
        if not frame:
            raise AppError("FRAME_NOT_FOUND", "The requested frame does not exist.", 404)
        return frame

    def _valid_labels(self, project_id: int, ids: list[int]) -> list[int]:
        valid = list(
            self.session.scalars(
                select(Label.id).where(Label.project_id == project_id, Label.id.in_(ids))
            )
        )
        if len(valid) != len(set(ids)):
            raise AppError(
                "LABEL_NOT_FOUND", "One or more labels do not exist in this project.", 404
            )
        return valid


class ReviewSessionService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, project_id: int) -> ReviewSession:
        session = self.session.scalar(
            select(ReviewSession).where(ReviewSession.project_id == project_id)
        )
        if not session:
            session = ReviewSession(project_id=project_id)
            self.session.add(session)
            try:
                self.session.commit()
                self.session.refresh(session)
            except IntegrityError:
                # Two browser requests can initialize the same project at once.
                # The unique constraint selects the winner; recover the row it made.
                self.session.rollback()
                session = self.session.scalar(
                    select(ReviewSession).where(ReviewSession.project_id == project_id)
                )
                if session is None:
                    raise
        return session

    def update(self, project_id: int, payload: ReviewSessionUpdate) -> ReviewSession:
        session = self.get(project_id)
        for key, value in payload.model_dump(
            exclude_unset=True, exclude={"active_filters"}
        ).items():
            setattr(session, key, value)
        if payload.active_filters is not None:
            session.active_filters_json = json.dumps(payload.active_filters)
        self.session.commit()
        self.session.refresh(session)
        return session

    @staticmethod
    def serialize(session: ReviewSession) -> ReviewSessionRead:
        return ReviewSessionRead(
            id=session.id,
            project_id=session.project_id,
            video_id=session.video_id,
            last_frame_id=session.last_frame_id,
            active_filters=json.loads(session.active_filters_json),
            gallery_position=session.gallery_position,
            thumbnail_size=session.thumbnail_size,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
