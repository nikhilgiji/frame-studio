import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { Link, useParams } from "react-router-dom";

import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { LabelManager } from "../components/LabelManager";
import { ExportPanel } from "../components/ExportPanel";
import { VideoImport } from "../components/VideoImport";
import { VideoList } from "../components/VideoList";
import { getProject } from "../services/projects";

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = Number(projectId);
  useEffect(() => {
    localStorage.setItem("vision-curator:last-project", String(id));
  }, [id]);
  const project = useQuery({
    queryKey: ["project", id],
    queryFn: ({ signal }) => getProject(id, signal),
    enabled: Number.isInteger(id),
  });

  if (project.isLoading)
    return (
      <main>
        <LoadingState label="Opening project" />
      </main>
    );
  if (project.error)
    return (
      <main>
        <ErrorState message={project.error.message} />
      </main>
    );
  return (
    <main className="project-detail">
      <Link to="/projects" className="back-link">
        ← All projects
      </Link>
      <p className="eyebrow">Active project</p>
      <h2>{project.data?.name}</h2>
      <p>{project.data?.description || "No description"}</p>
      <Link className="primary-link" to={`/projects/${id}/gallery`}>
        Open frame gallery →
      </Link>
      {project.data && (
        <>
          <ExportPanel projectId={project.data.id} />
          <LabelManager projectId={project.data.id} />
          <VideoImport projectId={project.data.id} />
          <VideoList projectId={project.data.id} />
        </>
      )}
    </main>
  );
}
