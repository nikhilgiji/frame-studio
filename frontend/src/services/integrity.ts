import { apiRequest } from "./api";

export interface IntegrityIssue {
  code: string;
  message: string;
  path: string | null;
  entity_type: string;
  entity_id: number;
  repairable: boolean;
  repaired: boolean;
}
export interface IntegrityReport {
  project_id: number;
  checked_videos: number;
  checked_frames: number;
  issue_count: number;
  repaired_count: number;
  issues: IntegrityIssue[];
}
export const runIntegrityCheck = async (
  projectId: number,
  repairThumbnails: boolean,
) =>
  (
    await apiRequest<{ data: IntegrityReport }>(
      `/projects/${projectId}/integrity-check`,
      {
        method: "POST",
        body: JSON.stringify({ repair_thumbnails: repairThumbnails }),
      },
    )
  ).data;
