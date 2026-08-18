import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  cancelJob,
  clearCompletedJobs,
  createThumbnailJob,
  listJobs,
  retryJob,
} from "../services/jobs";

export function JobHistory({ projectId }: { projectId: number }) {
  const client = useQueryClient();
  const jobs = useQuery({
    queryKey: ["jobs", projectId],
    queryFn: ({ signal }) => listJobs(projectId, signal),
    refetchInterval: (query) =>
      query.state.data?.some((job) =>
        ["pending", "running", "cancelling"].includes(job.status),
      )
        ? 500
        : false,
  });
  const refresh = () =>
    client.invalidateQueries({ queryKey: ["jobs", projectId] });
  const retry = useMutation({
    mutationFn: ({ kind, id }: { kind: string; id: number }) =>
      retryJob(kind, id),
    onSuccess: refresh,
  });
  return (
    <details className="job-history">
      <summary>
        <span>Background jobs</span>
        <small>Extraction, export, and thumbnail activity</small>
      </summary>
      <div className="panel-actions">
        <button
          onClick={() => void clearCompletedJobs(projectId).then(refresh)}
        >
          Clear completed
        </button>
        <button
          onClick={() => void createThumbnailJob(projectId).then(refresh)}
        >
          Regenerate thumbnails
        </button>
      </div>
      {!jobs.data?.length && <p>No background jobs yet.</p>}
      {jobs.data?.map((job) => (
        <article key={job.key}>
          <strong>{job.kind}</strong>
          <span>{job.status}</span>
          <progress max="100" value={job.progress} />
          <span>{Math.round(job.progress)}%</span>
          {job.error_message && <span role="alert">{job.error_message}</span>}
          {job.retryable && (
            <button
              onClick={() => retry.mutate({ kind: job.kind, id: job.id })}
            >
              Retry
            </button>
          )}
          {["pending", "running"].includes(job.status) && (
            <button
              onClick={() => void cancelJob(job.kind, job.id).then(refresh)}
            >
              Cancel
            </button>
          )}
        </article>
      ))}
    </details>
  );
}
