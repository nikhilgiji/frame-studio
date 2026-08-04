import { apiRequest } from "./api";
import type { Frame, FramePage, VideoTimeline } from "../types/frame";

export const apiBase =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
export async function listFrames(
  projectId: number,
  page: number,
  pageSize: number,
  filters: URLSearchParams,
  signal?: AbortSignal,
) {
  const params = new URLSearchParams(filters);
  params.set("page", String(page));
  params.set("page_size", String(pageSize));
  return apiRequest<FramePage>(`/projects/${projectId}/frames?${params}`, {
    signal,
  });
}
export const thumbnailUrl = (id: number) => `${apiBase}/frames/${id}/thumbnail`;
export const imageUrl = (id: number) => `${apiBase}/frames/${id}/image`;
export const getTimeline = async (videoId: number, signal?: AbortSignal) =>
  (
    await apiRequest<{ data: VideoTimeline }>(`/videos/${videoId}/timeline`, {
      signal,
    })
  ).data;
export const nearestFrame = async (
  videoId: number,
  target: { timestamp?: number; frame_number?: number },
) => {
  const params = new URLSearchParams();
  if (target.timestamp !== undefined)
    params.set("timestamp", String(target.timestamp));
  if (target.frame_number !== undefined)
    params.set("frame_number", String(target.frame_number));
  return (
    await apiRequest<{ data: Frame }>(
      `/videos/${videoId}/frames/nearest?${params}`,
    )
  ).data;
};
export const getFrame = async (id: number) =>
  (await apiRequest<{ data: Frame }>(`/frames/${id}`)).data;
