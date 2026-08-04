import { useState, type FormEvent } from "react";

import type { Project, ProjectInput } from "../types/project";

export function ProjectForm({
  project,
  busy,
  error,
  onSubmit,
  onCancel,
}: {
  project?: Project;
  busy: boolean;
  error?: string;
  onSubmit: (input: ProjectInput) => void;
  onCancel?: () => void;
}) {
  const [name, setName] = useState(project?.name ?? "");
  const [description, setDescription] = useState(project?.description ?? "");

  function submit(event: FormEvent) {
    event.preventDefault();
    const cleanName = name.trim();
    if (cleanName)
      onSubmit({ name: cleanName, description: description.trim() });
  }

  return (
    <form className="project-form" onSubmit={submit}>
      <label>
        Project name
        <input
          autoFocus
          value={name}
          maxLength={120}
          required
          onChange={(event) => setName(event.target.value)}
        />
      </label>
      <label>
        Description
        <textarea
          value={description}
          maxLength={4000}
          rows={3}
          onChange={(event) => setDescription(event.target.value)}
        />
      </label>
      {error && (
        <div className="inline-error" role="alert">
          {error}
        </div>
      )}
      <div className="form-actions">
        {onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
        <button type="submit" disabled={busy || !name.trim()}>
          {busy ? "Saving…" : project ? "Save changes" : "Create project"}
        </button>
      </div>
    </form>
  );
}
