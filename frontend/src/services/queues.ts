import { apiRequest } from "./api";

export interface ReviewQueue {
  id: number;
  project_id: number;
  name: string;
  queue_type: string;
  filters: Record<string, unknown>;
  position: number;
  current_frame_id: number | null;
  total: number;
  reviewed: number;
  remaining: number;
  completion_percentage: number;
  created_at: string;
  updated_at: string;
}
export const listQueues = async (projectId: number, signal?: AbortSignal) =>
  (
    await apiRequest<{ data: ReviewQueue[] }>(
      `/projects/${projectId}/review-queues`,
      { signal },
    )
  ).data;
export const createQueue = async (
  projectId: number,
  input: {
    name: string;
    queue_type: string;
    filters: Record<string, string | string[]>;
    random_limit?: number;
  },
) =>
  (
    await apiRequest<{ data: ReviewQueue }>(
      `/projects/${projectId}/review-queues`,
      { method: "POST", body: JSON.stringify(input) },
    )
  ).data;
export const updateQueue = async (id: number, position: number) =>
  (
    await apiRequest<{ data: ReviewQueue }>(`/review-queues/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ position }),
    })
  ).data;
