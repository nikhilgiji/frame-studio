import { apiRequest } from "./api";
import type { FramePage } from "../types/frame";

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
