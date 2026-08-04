import { useEffect, useState, type WheelEvent } from "react";

import { imageUrl } from "../services/frames";
import type { ReviewChanges } from "../services/review";
import type { Frame } from "../types/frame";
import { normalizedKey, useShortcuts } from "../services/shortcuts";

interface Props {
  frames: Frame[];
  index: number;
  onIndex: (index: number) => void;
  onClose: () => void;
  onReview: (frame: Frame, changes: ReviewChanges) => void;
}

export function FrameViewer({
  frames,
  index,
  onIndex,
  onClose,
  onReview,
}: Props) {
  const [zoom, setZoom] = useState(1);
  const [original, setOriginal] = useState(false);
  const [imageError, setImageError] = useState(false);
  const shortcuts = useShortcuts();
  const frame = frames[index];
  useEffect(() => {
    function key(event: KeyboardEvent) {
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      )
        return;
      const pressed = normalizedKey(event.key);
      if (
        [shortcuts.previous, shortcuts.previousAlt]
          .map(normalizedKey)
          .includes(pressed)
      )
        onIndex(Math.max(0, index - 1));
      if (
        [shortcuts.next, shortcuts.nextAlt].map(normalizedKey).includes(pressed)
      )
        onIndex(Math.min(frames.length - 1, index + 1));
      if (pressed === normalizedKey(shortcuts.closeViewer)) onClose();
      if (pressed === normalizedKey(shortcuts.favorite))
        onReview(frame, { favorite: !frame.favorite });
      if (pressed === normalizedKey(shortcuts.reject))
        onReview(frame, { rejected: !frame.rejected });
      if (pressed === normalizedKey(shortcuts.reviewed)) {
        event.preventDefault();
        onReview(frame, {
          review_status:
            frame.review_status === "reviewed" ? "unreviewed" : "reviewed",
        });
      }
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [frame, frames.length, index, onClose, onIndex, onReview, shortcuts]);
  useEffect(() => {
    setZoom(1);
    setOriginal(false);
    setImageError(false);
  }, [frame.id]);
  function wheel(event: WheelEvent) {
    event.preventDefault();
    setZoom((value) =>
      Math.min(8, Math.max(0.2, value * (event.deltaY < 0 ? 1.15 : 0.87))),
    );
  }
  return (
    <div
      className="viewer"
      role="dialog"
      aria-label={`Frame ${frame.frame_number}`}
    >
      <div className="viewer-top">
        <div>
          <strong>Frame {frame.frame_number}</strong>
          <span>
            {frame.video_filename} · {frame.timestamp_seconds.toFixed(3)}s ·{" "}
            {frame.width}×{frame.height} · {frame.review_status}
          </span>
          <span>
            {frame.labels.map((label) => label.name).join(", ") || "Unlabeled"}
          </span>
        </div>
        <div>
          <button
            onClick={() => onReview(frame, { favorite: !frame.favorite })}
          >
            Favorite
          </button>
          <button
            onClick={() => onReview(frame, { rejected: !frame.rejected })}
          >
            Reject
          </button>
          <button onClick={() => setZoom((z) => z / 1.25)}>−</button>
          <button onClick={() => setZoom(1)}>Fit</button>
          <button
            onClick={() => {
              setOriginal(true);
              setZoom(1);
            }}
          >
            Original size
          </button>
          <button onClick={() => setZoom((z) => z * 1.25)}>+</button>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
      <div className="viewer-canvas" onWheel={wheel}>
        {imageError ? (
          <div role="alert">The full-resolution image is missing.</div>
        ) : (
          <img
            src={imageUrl(frame.id)}
            alt={`Full resolution frame ${frame.frame_number}`}
            onError={() => setImageError(true)}
            style={{
              transform: `scale(${zoom})`,
              maxWidth: original ? "none" : "90vw",
              maxHeight: original ? "none" : "80vh",
            }}
          />
        )}
      </div>
      <button
        className="viewer-prev"
        disabled={!index}
        onClick={() => onIndex(index - 1)}
      >
        Previous
      </button>
      <button
        className="viewer-next"
        disabled={index === frames.length - 1}
        onClick={() => onIndex(index + 1)}
      >
        Next
      </button>
    </div>
  );
}
