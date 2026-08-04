export interface Project {
  id: number;
  name: string;
  description: string;
  root_path: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectInput {
  name: string;
  description: string;
}

export interface ProjectEnvelope {
  data: Project;
  error: null;
}
export interface ProjectListEnvelope {
  data: Project[];
  error: null;
}
