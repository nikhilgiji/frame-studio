import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { ErrorState } from "./ErrorState";
import { ExtractionPanel } from "./ExtractionPanel";
import { LoadingState } from "./LoadingState";
import { deleteVideo, listVideos } from "../services/videos";
import type { Video } from "../types/video";

function size(bytes: number) {
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
function duration(seconds: number) {
  return `${Math.floor(seconds / 60)}:${String(Math.round(seconds % 60)).padStart(2, "0")}`;
}

export function VideoList({ projectId }: { projectId: number }) {
  const queryClient = useQueryClient();
  const [extracting, setExtracting] = useState<number | null>(null);
  const videos = useQuery({
    queryKey: ["videos", projectId],
    queryFn: ({ signal }) => listVideos(projectId, signal),
  });
  const remove = useMutation({
    mutationFn: deleteVideo,
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ["videos", projectId] }),
  });
  function confirmDelete(video: Video) {
    if (window.confirm(`Delete the imported copy of “${video.filename}”?`))
      remove.mutate(video.id);
  }
  if (videos.isLoading) return <LoadingState label="Loading videos" />;
  if (videos.error)
    return (
      <ErrorState
        message={videos.error.message}
        onRetry={() => void videos.refetch()}
      />
    );
  if (!videos.data?.length)
    return (
      <div className="empty-state">
        <h3>No videos imported</h3>
        <p>Choose individual videos or a folder above.</p>
      </div>
    );
  return (
    <section className="video-list">
      {videos.data.map((video) => (
        <div key={video.id}>
          <article>
            <div className="video-icon">▶</div>
            <div className="video-name">
              <h3>{video.filename}</h3>
              <p>
                {video.width}×{video.height} · {video.fps.toFixed(2)} FPS ·{" "}
                {duration(video.duration_seconds)}
              </p>
            </div>
            <div className="video-stat">
              <span>{video.frame_count.toLocaleString()}</span> frames
            </div>
            <div className="video-stat">
              <span>{size(video.file_size)}</span> {video.codec}
            </div>
            <span className="ready">{video.status}</span>
            <button onClick={() => setExtracting(video.id)}>
              Extract frames
            </button>
            <button className="danger" onClick={() => confirmDelete(video)}>
              Delete
            </button>
          </article>
          {extracting === video.id && (
            <ExtractionPanel
              videoId={video.id}
              onClose={() => setExtracting(null)}
            />
          )}
        </div>
      ))}
    </section>
  );
}
