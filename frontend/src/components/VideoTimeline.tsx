import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { getTimeline, nearestFrame, thumbnailUrl } from "../services/frames";
import type { Frame } from "../types/frame";

export function VideoTimeline({
  videoId,
  current,
  onOpen,
}: {
  videoId: number;
  current?: Frame;
  onOpen: (frame: Frame) => void;
}) {
  const timeline = useQuery({
    queryKey: ["timeline", videoId],
    queryFn: ({ signal }) => getTimeline(videoId, signal),
  });
  const [timestamp, setTimestamp] = useState(0);
  const [frameNumber, setFrameNumber] = useState(0);
  async function jump(target: { timestamp?: number; frame_number?: number }) {
    onOpen(await nearestFrame(videoId, target));
  }
  if (!timeline.data) return null;
  const duration = Math.max(0, timeline.data.duration_seconds);
  return (
    <section className="video-timeline" aria-label="Video timeline">
      <header>
        <strong>Timeline</strong>
        <span>{(current?.timestamp_seconds ?? timestamp).toFixed(3)}s</span>
        <span>{timeline.data.extracted_count} extraction points</span>
      </header>
      <input
        aria-label="Timeline position"
        type="range"
        min="0"
        max={duration}
        step="0.001"
        value={current?.timestamp_seconds ?? timestamp}
        onChange={(event) => setTimestamp(Number(event.target.value))}
        onMouseUp={() => void jump({ timestamp })}
        onKeyUp={(event) => {
          if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key))
            void jump({ timestamp });
        }}
      />
      <div className="timeline-markers">
        {timeline.data.markers.map((marker) => (
          <button
            key={marker.frame_id}
            title={`${marker.timestamp_seconds.toFixed(3)}s${marker.labeled ? " · labeled" : ""}${marker.rejected ? " · rejected" : ""}`}
            className={
              marker.rejected ? "rejected" : marker.labeled ? "labeled" : ""
            }
            onClick={() => void jump({ timestamp: marker.timestamp_seconds })}
          >
            <img src={thumbnailUrl(marker.frame_id)} alt="" loading="lazy" />
          </button>
        ))}
      </div>
      <div className="timeline-jumps">
        <button onClick={() => void jump({ timestamp: 0 })}>Beginning</button>
        <button onClick={() => void jump({ timestamp: duration / 2 })}>
          Middle
        </button>
        <button onClick={() => void jump({ timestamp: duration })}>End</button>
        <label>
          Timestamp
          <input
            type="number"
            min="0"
            max={duration}
            step="0.001"
            value={timestamp}
            onChange={(event) => setTimestamp(Number(event.target.value))}
          />
          <button onClick={() => void jump({ timestamp })}>Jump</button>
        </label>
        <label>
          Frame number
          <input
            type="number"
            min="0"
            value={frameNumber}
            onChange={(event) => setFrameNumber(Number(event.target.value))}
          />
          <button onClick={() => void jump({ frame_number: frameNumber })}>
            Jump
          </button>
        </label>
      </div>
    </section>
  );
}
