export interface ExportJob {
  id: number;
  project_id: number;
  destination_path: string;
  export_mode: string;
  status: string;
  progress: number;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}
