import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import {
  cancelExport,
  createExport,
  getExport,
  type ExportInput,
} from "../services/exports";

export function ExportPanel({
  projectId,
  selectedIds = [],
  allFiltered = false,
  filters = {},
}: {
  projectId: number;
  selectedIds?: number[];
  allFiltered?: boolean;
  filters?: Record<string, string | string[]>;
}) {
  const [open, setOpen] = useState(false);
  const [jobId, setJobId] = useState<number | null>(null);
  const [name, setName] = useState("dataset");
  const [mode, setMode] = useState<ExportInput["export_mode"]>(
    selectedIds.length || allFiltered ? "selected" : "favorites",
  );
  const [multi, setMulti] =
    useState<ExportInput["multi_label_mode"]>("copy_each");
  const [conflict, setConflict] = useState<ExportInput["conflict"]>("rename");
  const create = useMutation({
    mutationFn: (input: ExportInput) => createExport(projectId, input),
    onSuccess: (job) => setJobId(job.id),
  });
  const job = useQuery({
    queryKey: ["export", jobId],
    queryFn: ({ signal }) => getExport(jobId!, signal),
    enabled: jobId !== null,
    refetchInterval: (query) =>
      ["pending", "running", "cancelling"].includes(
        query.state.data?.status ?? "",
      )
        ? 500
        : false,
  });
  const cancel = useMutation({
    mutationFn: cancelExport,
    onSuccess: () => void job.refetch(),
  });
  if (!open)
    return <button onClick={() => setOpen(true)}>Export dataset</button>;
  return (
    <section className="export-panel">
      <h3>Export dataset</h3>
      {!jobId ? (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            create.mutate({
              destination_name: name,
              export_mode: mode,
              frame_ids: selectedIds,
              all_filtered: allFiltered,
              filters,
              label_ids: [],
              multi_label_mode: multi,
              conflict,
            });
          }}
        >
          <label>
            Folder name
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              pattern="[A-Za-z0-9._ \\-]+"
              required
            />
          </label>
          <label>
            Mode
            <select
              value={mode}
              onChange={(e) =>
                setMode(e.target.value as ExportInput["export_mode"])
              }
            >
              {selectedIds.length > 0 && (
                <option value="selected">Selected frames</option>
              )}
              <option value="favorites">Favorites</option>
              <option value="reviewed">Reviewed</option>
              <option value="label_folders">Label folders</option>
              <option value="manifest">Manifest only</option>
            </select>
          </label>
          <label>
            Multi-label
            <select
              value={multi}
              onChange={(e) =>
                setMulti(e.target.value as ExportInput["multi_label_mode"])
              }
            >
              <option value="copy_each">Copy into every label folder</option>
              <option value="manifest_only">
                Images once, labels in manifest
              </option>
            </select>
          </label>
          <label>
            Existing files
            <select
              value={conflict}
              onChange={(e) =>
                setConflict(e.target.value as ExportInput["conflict"])
              }
            >
              <option value="rename">Rename</option>
              <option value="skip">Skip</option>
              <option value="overwrite">Overwrite</option>
            </select>
          </label>
          <button disabled={create.isPending}>Start export</button>
          <button type="button" onClick={() => setOpen(false)}>
            Close
          </button>
          {create.error && <span role="alert">{create.error.message}</span>}
        </form>
      ) : (
        <div className="job-progress">
          <strong>{job.data?.status ?? "Starting"}</strong>
          <progress value={job.data?.progress ?? 0} max="100" />
          <span>{Math.round(job.data?.progress ?? 0)}%</span>
          {job.data?.status === "completed" && (
            <span>Saved to {job.data.destination_path}</span>
          )}
          {job.data?.error_message && (
            <span role="alert">{job.data.error_message}</span>
          )}
          {["pending", "running"].includes(job.data?.status ?? "") && (
            <button onClick={() => cancel.mutate(jobId)}>Cancel</button>
          )}
          <button onClick={() => setOpen(false)}>Close</button>
        </div>
      )}
    </section>
  );
}
