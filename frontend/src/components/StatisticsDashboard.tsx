import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { getStatistics } from "../services/statistics";
import { listVideos } from "../services/videos";

export function StatisticsDashboard({ projectId }: { projectId: number }) {
  const [videoId, setVideoId] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const filters = {
    video_id: videoId ? Number(videoId) : undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
  };
  const statistics = useQuery({
    queryKey: ["statistics", projectId, filters],
    queryFn: ({ signal }) => getStatistics(projectId, filters, signal),
  });
  const videos = useQuery({
    queryKey: ["videos", projectId],
    queryFn: ({ signal }) => listVideos(projectId, signal),
  });
  const data = statistics.data;
  const metric = (name: string, value: number) => (
    <div>
      <dt>{name}</dt>
      <dd>{value.toLocaleString()}</dd>
    </div>
  );
  const bars = (values: { id?: number; name: string; count: number }[]) => {
    const max = Math.max(1, ...values.map((value) => value.count));
    return values.map((value) => (
      <div
        className="chart-row"
        key={`${value.id ?? value.name}-${value.name}`}
      >
        <span>{value.name}</span>
        <i style={{ width: `${(value.count / max) * 100}%` }} />
        <b>{value.count}</b>
      </div>
    ));
  };
  return (
    <details className="statistics-dashboard">
      <summary>Statistics dashboard</summary>
      <div className="statistics-filters">
        <select
          aria-label="Statistics video"
          value={videoId}
          onChange={(e) => setVideoId(e.target.value)}
        >
          <option value="">All videos</option>
          {videos.data?.map((video) => (
            <option value={video.id} key={video.id}>
              {video.filename}
            </option>
          ))}
        </select>
        <input
          aria-label="Statistics from date"
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
        />
        <input
          aria-label="Statistics to date"
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
        />
      </div>
      {data && (
        <>
          <dl className="metric-grid">
            {metric("Projects", data.total_projects)}
            {metric("Videos", data.total_videos)}
            {metric("Frames", data.total_frames)}
            {metric("Reviewed", data.reviewed_frames)}
            {metric("Unreviewed", data.unreviewed_frames)}
            {metric("Rejected", data.rejected_frames)}
            {metric("Favorites", data.favorite_frames)}
            {metric("Extraction jobs", data.extraction_jobs)}
            {metric("Export jobs", data.export_jobs)}
          </dl>
          <div className="chart-grid">
            <section>
              <h4>Label distribution</h4>
              {bars(data.frames_per_label)}
            </section>
            <section>
              <h4>Frames per video</h4>
              {bars(data.frames_per_video)}
            </section>
            <section>
              <h4>Review status</h4>
              {bars([
                { name: "Reviewed", count: data.reviewed_frames },
                { name: "Unreviewed", count: data.unreviewed_frames },
                { name: "Rejected", count: data.rejected_frames },
              ])}
            </section>
            <section>
              <h4>Review progress</h4>
              {bars(
                data.review_progress.map((row) => ({
                  name: row.date,
                  count: row.count,
                })),
              )}
            </section>
          </div>
        </>
      )}
    </details>
  );
}
