import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { listHistory, redoAction, undoAction } from "../services/history";

export function ActionHistoryPanel({ projectId }: { projectId: number }) {
  const client = useQueryClient();
  const history = useQuery({
    queryKey: ["action-history", projectId],
    queryFn: ({ signal }) => listHistory(projectId, signal),
  });
  const refresh = async () => {
    await Promise.all([
      client.invalidateQueries({ queryKey: ["action-history", projectId] }),
      client.invalidateQueries({ queryKey: ["frames", projectId] }),
      client.invalidateQueries({ queryKey: ["statistics", projectId] }),
    ]);
  };
  const undo = useMutation({
    mutationFn: () => undoAction(projectId),
    onSuccess: refresh,
  });
  const redo = useMutation({
    mutationFn: () => redoAction(projectId),
    onSuccess: refresh,
  });
  const actions = history.data ?? [];
  return (
    <details className="action-history">
      <summary>Action history</summary>
      <button
        disabled={!actions.some((action) => action.status === "applied")}
        onClick={() => undo.mutate()}
      >
        Undo
      </button>
      <button
        disabled={!actions.some((action) => action.status === "undone")}
        onClick={() => redo.mutate()}
      >
        Redo
      </button>
      {actions.map((action) => (
        <p key={action.id} className={action.status}>
          <span>{action.description}</span> <small>{action.status}</small>
        </p>
      ))}
    </details>
  );
}
