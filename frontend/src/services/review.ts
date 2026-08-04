import { apiRequest } from "./api";
import type { Frame } from "../types/frame";
import type { Label, ReviewSession } from "../types/review";

export const listLabels = async (projectId: number, signal?: AbortSignal) =>
  (
    await apiRequest<{ data: Label[] }>(`/projects/${projectId}/labels`, {
      signal,
    })
  ).data;
export const createLabel = async (
  projectId: number,
  input: { name: string; shortcut: string | null; color: string },
) =>
  (
    await apiRequest<{ data: Label }>(`/projects/${projectId}/labels`, {
      method: "POST",
      body: JSON.stringify(input),
    })
  ).data;
export const updateLabel = async (
  id: number,
  input: Partial<
    Pick<Label, "name" | "shortcut" | "color" | "description" | "position">
  >,
) =>
  (
    await apiRequest<{ data: Label }>(`/labels/${id}`, {
      method: "PATCH",
      body: JSON.stringify(input),
    })
  ).data;
export const deleteLabel = (id: number) =>
  apiRequest<void>(`/labels/${id}`, { method: "DELETE" });
export const assignLabels = async (frameId: number, labelIds: number[]) =>
  (
    await apiRequest<{ data: Frame }>(`/frames/${frameId}/labels`, {
      method: "POST",
      body: JSON.stringify({ label_ids: labelIds }),
    })
  ).data;
export const removeLabel = async (frameId: number, labelId: number) =>
  (
    await apiRequest<{ data: Frame }>(`/frames/${frameId}/labels/${labelId}`, {
      method: "DELETE",
    })
  ).data;
export const bulkLabels = (
  frameIds: number[],
  labelIds: number[],
  action: "assign" | "remove",
) =>
  apiRequest<void>("/frames/bulk-label", {
    method: "POST",
    body: JSON.stringify({ frame_ids: frameIds, label_ids: labelIds, action }),
  });
export type ReviewChanges = {
  review_status?: string;
  favorite?: boolean;
  rejected?: boolean;
};
export const reviewFrame = async (frameId: number, changes: ReviewChanges) =>
  (
    await apiRequest<{ data: Frame }>(`/frames/${frameId}/review`, {
      method: "PATCH",
      body: JSON.stringify(changes),
    })
  ).data;
export const bulkReview = (frameIds: number[], changes: ReviewChanges) =>
  apiRequest<void>("/frames/bulk-review", {
    method: "POST",
    body: JSON.stringify({ frame_ids: frameIds, ...changes }),
  });
export interface BatchTarget {
  frame_ids: number[];
  all_filtered: boolean;
  filters: Record<string, string | string[]>;
}
export const filteredBulkLabels = (
  projectId: number,
  target: BatchTarget,
  labelIds: number[],
  action: "assign" | "remove",
) =>
  apiRequest<{ affected_count: number }>(
    `/projects/${projectId}/frames/bulk-label`,
    {
      method: "POST",
      body: JSON.stringify({
        ...target,
        label_ids: labelIds,
        action,
      }),
    },
  );
export const filteredBulkReview = (
  projectId: number,
  target: BatchTarget,
  changes: ReviewChanges,
) =>
  apiRequest<{ affected_count: number }>(
    `/projects/${projectId}/frames/bulk-review`,
    {
      method: "POST",
      body: JSON.stringify({ ...target, ...changes }),
    },
  );
export const getSession = async (projectId: number, signal?: AbortSignal) =>
  (
    await apiRequest<{ data: ReviewSession }>(
      `/projects/${projectId}/review-session`,
      { signal },
    )
  ).data;
export const saveSession = async (
  projectId: number,
  changes: Record<string, unknown>,
) =>
  (
    await apiRequest<{ data: ReviewSession }>(
      `/projects/${projectId}/review-session`,
      { method: "PATCH", body: JSON.stringify(changes) },
    )
  ).data;
