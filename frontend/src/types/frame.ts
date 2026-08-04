import type { Label } from "./review";
export interface Frame {
  id: number;
  project_id: number;
  video_id: number;
  video_filename: string;
  frame_number: number;
  timestamp_seconds: number;
  width: number;
  height: number;
  review_status: string;
  favorite: boolean;
  rejected: boolean;
  reviewed_at: string | null;
  created_at: string;
  labels: Label[];
}
export interface FramePage {
  items: Frame[];
  page: number;
  page_size: number;
  total: number;
  has_next: boolean;
}
