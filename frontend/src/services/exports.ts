import { apiRequest } from "./api";
import type { ExportJob } from "../types/export";

export interface ExportInput {
  destination_name: string;
  export_mode:
    "label_folders" | "selected" | "favorites" | "reviewed" | "manifest";
  frame_ids: number[];
  all_filtered?: boolean;
  filters?: Record<string, string | string[]>;
  label_ids: number[];
  multi_label_mode: "copy_each" | "manifest_only";
  conflict: "skip" | "overwrite" | "rename";
}
export const createExport = async (projectId: number, input: ExportInput) =>
  (
    await apiRequest<{ data: ExportJob }>(
      `/projects/${projectId}/export-jobs`,
      { method: "POST", body: JSON.stringify(input) },
    )
  ).data;
export const getExport = async (id: number, signal?: AbortSignal) =>
  (await apiRequest<{ data: ExportJob }>(`/export-jobs/${id}`, { signal }))
    .data;
export const cancelExport = async (id: number) =>
  (
    await apiRequest<{ data: ExportJob }>(`/export-jobs/${id}/cancel`, {
      method: "POST",
    })
  ).data;
