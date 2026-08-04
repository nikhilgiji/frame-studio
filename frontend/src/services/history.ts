import { apiRequest } from "./api";

export interface ActionHistory {
  id: number;
  project_id: number;
  action_type: string;
  description: string;
  status: string;
  created_at: string;
}
export const listHistory = async (projectId: number, signal?: AbortSignal) =>
  (
    await apiRequest<{ data: ActionHistory[] }>(
      `/projects/${projectId}/action-history`,
      { signal },
    )
  ).data;
export const undoAction = async (projectId: number) =>
  (
    await apiRequest<{ data: ActionHistory }>(
      `/projects/${projectId}/action-history/undo`,
      { method: "POST" },
    )
  ).data;
export const redoAction = async (projectId: number) =>
  (
    await apiRequest<{ data: ActionHistory }>(
      `/projects/${projectId}/action-history/redo`,
      { method: "POST" },
    )
  ).data;
