import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { ReviewWorkflow } from "../components/ReviewWorkflow";
import { StatisticsDashboard } from "../components/StatisticsDashboard";
import { LabelManager } from "../components/LabelManager";
import { JobHistory } from "../components/JobHistory";
import { IntegrityPanel } from "../components/IntegrityPanel";
import { ExportPanel } from "../components/ExportPanel";
import { VideoImport } from "../components/VideoImport";
import { VideoList } from "../components/VideoList";
import { getProject } from "../services/projects";

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = Number(projectId);
  const [activePanel, setActivePanel] = useState<
    "overview" | "labels" | "videos"
  >("overview");
  useEffect(() => {
    localStorage.setItem("vision-curator:last-project", String(id));
  }, [id]);
  const project = useQuery({
    queryKey: ["project", id],
    queryFn: ({ signal }) => getProject(id, signal),
    enabled: Number.isInteger(id),
  });
  useEffect(() => {
    if (!project.data) return;
    const key = "vision-curator:recent-projects";
    let recent: { id: number; name: string }[] = [];
    try {
      recent = JSON.parse(localStorage.getItem(key) ?? "[]");
    } catch {
      recent = [];
    }
    localStorage.setItem(
      key,
      JSON.stringify(
        [
          { id: project.data.id, name: project.data.name },
          ...recent.filter((item) => item.id !== project.data?.id),
        ].slice(0, 5),
      ),
    );
  }, [project.data]);

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
      <Link to="/projects" className="back-link project-back-link">
        <span aria-hidden="true">←</span> All projects
      </Link>
      <section className="project-hero">
        <div className="project-hero-copy">
          <h2>{project.data?.name}</h2>
          <p className="project-description">
            {project.data?.description || "No project description yet."}
          </p>
        </div>
        <div className="project-hero-actions">
          <Link className="button-link primary" to={`/projects/${id}/gallery`}>
            Open frame gallery <span aria-hidden="true">→</span>
          </Link>
          {project.data && <ExportPanel projectId={project.data.id} />}
        </div>
      </section>
      {project.data && (
        <>
          <nav className="workspace-tabs" aria-label="Project workspace">
            {(
              [
                ["overview", "Overview"],
                ["labels", "Labels"],
                ["videos", "Videos"],
              ] as const
            ).map(([panel, label]) => (
              <button
                key={panel}
                type="button"
                className={activePanel === panel ? "active" : ""}
                aria-current={activePanel === panel ? "page" : undefined}
                onClick={() => setActivePanel(panel)}
              >
                {label}
              </button>
            ))}
          </nav>

          {activePanel === "overview" && (
            <section
              className="dashboard-section"
              aria-labelledby="overview-heading"
            >
              <ReviewWorkflow
                projectId={project.data.id}
                onOpenVideos={() => setActivePanel("videos")}
              />
              <div className="section-heading">
                <h3 id="overview-heading">Project overview</h3>
                <p>
                  Track review progress, background work, and file integrity.
                </p>
              </div>
              <StatisticsDashboard projectId={project.data.id} />
              <div className="dashboard-utility-grid">
                <JobHistory projectId={project.data.id} />
                <IntegrityPanel projectId={project.data.id} />
              </div>
            </section>
          )}

          {activePanel === "labels" && (
            <section
              className="dashboard-section"
              aria-labelledby="organize-heading"
            >
              <div className="section-heading">
                <h3 id="organize-heading">Labels</h3>
                <p>Create a clear vocabulary before reviewing frames.</p>
              </div>
              <LabelManager projectId={project.data.id} />
            </section>
          )}

          {activePanel === "videos" && (
            <section
              className="dashboard-section"
              aria-labelledby="sources-heading"
            >
              <div className="section-heading">
                <h3 id="sources-heading">Videos</h3>
                <p>Import source media and control frame extraction.</p>
              </div>
              <VideoImport projectId={project.data.id} />
              <VideoList projectId={project.data.id} />
            </section>
          )}
        </>
      )}
    </main>
  );
}
