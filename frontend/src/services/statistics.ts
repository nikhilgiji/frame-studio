import { apiRequest } from "./api";

export interface NamedCount {
  id: number;
  name: string;
  count: number;
}
export interface ProjectStatistics {
  total_projects: number;
  total_videos: number;
  total_frames: number;
  reviewed_frames: number;
  unreviewed_frames: number;
  rejected_frames: number;
  favorite_frames: number;
  extraction_jobs: number;
  export_jobs: number;
  frames_per_label: NamedCount[];
  frames_per_video: NamedCount[];
  review_progress: { date: string; count: number }[];
}
export const getStatistics = async (
  projectId: number,
  filters: { video_id?: number; date_from?: string; date_to?: string },
  signal?: AbortSignal,
) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value));
  });
  return (
    await apiRequest<{ data: ProjectStatistics }>(
      `/projects/${projectId}/statistics?${params}`,
      { signal },
    )
  ).data;
};
