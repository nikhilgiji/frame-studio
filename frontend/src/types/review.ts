export interface Label {
  id: number;
  project_id: number;
  name: string;
  shortcut: string | null;
  color: string;
  description: string;
  position: number;
  created_at: string;
}
export interface ReviewSession {
  id: number;
  project_id: number;
  video_id: number | null;
  last_frame_id: number | null;
  active_filters: Record<string, unknown>;
  gallery_position: number;
  thumbnail_size: number;
  created_at: string;
  updated_at: string;
}
