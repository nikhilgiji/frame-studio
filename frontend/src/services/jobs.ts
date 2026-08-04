import { apiRequest } from "./api";

export interface UnifiedJob {
  key: string;
  id: number;
  project_id: number;
  kind: string;
  status: string;
  progress: number;
  error_message: string | null;
  retryable: boolean;
  created_at: string;
  completed_at: string | null;
}
export const listJobs = async (projectId: number, signal?: AbortSignal) =>
  (
    await apiRequest<{ data: UnifiedJob[] }>(`/projects/${projectId}/jobs`, {
      signal,
    })
  ).data;
export const retryJob = async (kind: string, id: number) =>
  (
    await apiRequest<{ data: UnifiedJob }>(`/jobs/${kind}/${id}/retry`, {
      method: "POST",
    })
  ).data;
export const cancelJob = async (kind: string, id: number) =>
  (
    await apiRequest<{ data: UnifiedJob }>(`/jobs/${kind}/${id}/cancel`, {
      method: "POST",
    })
  ).data;
export const createThumbnailJob = async (projectId: number) =>
  (
    await apiRequest<{ data: UnifiedJob }>(
      `/projects/${projectId}/thumbnail-jobs`,
      { method: "POST" },
    )
  ).data;
export const clearCompletedJobs = (projectId: number) =>
  apiRequest<{ cleared_count: number }>(
    `/projects/${projectId}/jobs/completed`,
    { method: "DELETE" },
  );
