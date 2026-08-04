import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { getFrame } from "../services/frames";
import { createQueue, listQueues, updateQueue } from "../services/queues";
import type { Frame } from "../types/frame";

export function ReviewQueuePanel({
  projectId,
  filters,
  onOpen,
}: {
  projectId: number;
  filters: Record<string, string | string[]>;
  onOpen: (frame: Frame) => void;
}) {
  const client = useQueryClient();
  const [name, setName] = useState("My review queue");
  const [kind, setKind] = useState("filtered");
  const queues = useQuery({
    queryKey: ["review-queues", projectId],
    queryFn: ({ signal }) => listQueues(projectId, signal),
  });
  const create = useMutation({
    mutationFn: () =>
      createQueue(projectId, {
        name,
        queue_type: kind,
        filters,
        random_limit: kind === "random" ? 100 : undefined,
      }),
    onSuccess: () =>
      client.invalidateQueries({ queryKey: ["review-queues", projectId] }),
  });
  async function move(queueId: number, position: number) {
    const queue = await updateQueue(queueId, position);
    await client.invalidateQueries({ queryKey: ["review-queues", projectId] });
    if (queue.current_frame_id) onOpen(await getFrame(queue.current_frame_id));
  }
  return (
    <details className="queue-panel">
      <summary>Review queues</summary>
      <div className="queue-create">
        <input
          aria-label="Queue name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <select
          aria-label="Queue type"
          value={kind}
          onChange={(e) => setKind(e.target.value)}
        >
          <option value="filtered">Current filters</option>
          <option value="unreviewed">All unreviewed</option>
          <option value="video">Current video</option>
          <option value="label">Current labels</option>
          <option value="rejected">Rejected</option>
          <option value="favorites">Favorites</option>
          <option value="random">Random sample (100)</option>
        </select>
        <button
          disabled={create.isPending || !name.trim()}
          onClick={() => create.mutate()}
        >
          Create queue
        </button>
      </div>
      {queues.data?.map((queue) => (
        <article key={queue.id} className="queue-row">
          <strong>{queue.name}</strong>
          <span>
            {queue.position + 1} / {queue.total}
          </span>
          <span>
            {queue.reviewed} reviewed · {queue.remaining} remaining
          </span>
          <progress max="100" value={queue.completion_percentage} />
          <button
            disabled={queue.position === 0}
            onClick={() => void move(queue.id, queue.position - 1)}
          >
            Previous
          </button>
          <button
            disabled={!queue.current_frame_id}
            onClick={() => void move(queue.id, queue.position)}
          >
            Resume
          </button>
          <button
            disabled={queue.position >= queue.total - 1}
            onClick={() => void move(queue.id, queue.position + 1)}
          >
            Next
          </button>
        </article>
      ))}
    </details>
  );
}
