export interface ExtractionJob {
  id: number;
  project_id: number;
  video_id: number;
  mode: string;
  mode_value: number;
  output_format: string;
  jpeg_quality: number;
  resize_width: number | null;
  resize_height: number | null;
  status: string;
  progress: number;
  processed_frames: number;
  total_frames: number;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}
export interface ExtractionInput {
  mode: "every_n_frames" | "frames_per_second" | "every_n_seconds";
  mode_value: number;
  output_format: "jpeg" | "png";
  jpeg_quality: number;
  resize_width: number | null;
  resize_height: number | null;
  overwrite: boolean;
}
