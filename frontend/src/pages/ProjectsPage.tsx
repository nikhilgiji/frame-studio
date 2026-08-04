import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { ProjectForm } from "../components/ProjectForm";
import { useToast } from "../components/toastContext";
import {
  createProject,
  deleteProject,
  listProjects,
  updateProject,
} from "../services/projects";
import type { Project, ProjectInput } from "../types/project";

function date(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function ProjectsPage() {
  const queryClient = useQueryClient();
  const { notify } = useToast();
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<Project | null>(null);
  const projects = useQuery({
    queryKey: ["projects"],
    queryFn: ({ signal }) => listProjects(signal),
  });
  const refresh = () =>
    queryClient.invalidateQueries({ queryKey: ["projects"] });
  const create = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      setShowCreate(false);
      notify("Project created");
      void refresh();
    },
  });
  const update = useMutation({
    mutationFn: ({ id, input }: { id: number; input: ProjectInput }) =>
      updateProject(id, input),
    onSuccess: () => {
      setEditing(null);
      notify("Project updated");
      void refresh();
    },
  });
  const remove = useMutation({
    mutationFn: deleteProject,
    onSuccess: () => {
      notify("Project record deleted", "info");
      void refresh();
    },
  });

  function confirmDelete(project: Project) {
    if (
      window.confirm(
        `Delete “${project.name}”? Project files will remain on disk.`,
      )
    )
      remove.mutate(project.id);
  }

  return (
    <main className="projects-page">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Workspaces</p>
          <h2>Projects</h2>
          <p>Create a focused home for each video dataset.</p>
        </div>
        <button onClick={() => setShowCreate(true)}>New project</button>
      </section>
      {showCreate && (
        <section className="form-card">
          <h3>Create project</h3>
          <ProjectForm
            busy={create.isPending}
            error={create.error?.message}
            onSubmit={(input) => create.mutate(input)}
            onCancel={() => setShowCreate(false)}
          />
        </section>
      )}
      {projects.isLoading && <LoadingState label="Loading projects" />}
      {projects.error && (
        <ErrorState
          message={projects.error.message}
          onRetry={() => void projects.refetch()}
        />
      )}
      {projects.data?.length === 0 && !showCreate && (
        <section className="empty-state">
          <h3>No projects yet</h3>
          <p>Create your first workspace to begin curating video frames.</p>
        </section>
      )}
      <section className="project-grid">
        {projects.data?.map((project) => (
          <article className="project-card" key={project.id}>
            {editing?.id === project.id ? (
              <ProjectForm
                project={project}
                busy={update.isPending}
                error={update.error?.message}
                onSubmit={(input) => update.mutate({ id: project.id, input })}
                onCancel={() => setEditing(null)}
              />
            ) : (
              <>
                <Link to={`/projects/${project.id}`}>
                  <h3>{project.name}</h3>
                </Link>
                <p>{project.description || "No description"}</p>
                <dl>
                  <div>
                    <dt>Created</dt>
                    <dd>{date(project.created_at)}</dd>
                  </div>
                  <div>
                    <dt>Modified</dt>
                    <dd>{date(project.updated_at)}</dd>
                  </div>
                </dl>
                <div className="card-actions">
                  <button
                    className="secondary"
                    onClick={() => setEditing(project)}
                  >
                    Edit
                  </button>
                  <button
                    className="danger"
                    onClick={() => confirmDelete(project)}
                  >
                    Delete
                  </button>
                </div>
              </>
            )}
          </article>
        ))}
      </section>
      {remove.error && <ErrorState message={remove.error.message} />}
    </main>
  );
}
