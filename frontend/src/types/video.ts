export interface Video {
  id: number;
  project_id: number;
  filename: string;
  source_path: string;
  stored_path: string;
  file_size: number;
  fps: number;
  duration_seconds: number;
  frame_count: number;
  width: number;
  height: number;
  codec: string;
  status: string;
  created_at: string;
}

export interface ImportIssue {
  filename: string;
  code: string;
  message: string;
}
export interface VideoImportResult {
  imported: Video[];
  skipped: ImportIssue[];
  errors: ImportIssue[];
}
