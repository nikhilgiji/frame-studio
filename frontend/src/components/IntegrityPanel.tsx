import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { runIntegrityCheck } from "../services/integrity";

export function IntegrityPanel({ projectId }: { projectId: number }) {
  const [repair, setRepair] = useState(true);
  const scan = useMutation({
    mutationFn: () => runIntegrityCheck(projectId, repair),
  });
  return (
    <details className="integrity-panel">
      <summary>File integrity</summary>
      <label>
        <input
          type="checkbox"
          checked={repair}
          onChange={(e) => setRepair(e.target.checked)}
        />
        Regenerate safe missing thumbnails
      </label>
      <button disabled={scan.isPending} onClick={() => scan.mutate()}>
        {scan.isPending ? "Scanning…" : "Run integrity check"}
      </button>
      {scan.data && (
        <div>
          <strong>
            {scan.data.issue_count} issues · {scan.data.repaired_count} repaired
          </strong>
          <p>
            {scan.data.checked_videos} videos and {scan.data.checked_frames}{" "}
            frames checked
          </p>
          {scan.data.issues.map((issue, index) => (
            <article key={`${issue.code}-${issue.entity_id}-${index}`}>
              <b>{issue.code}</b> {issue.message}
              {issue.repaired && <span> Repaired</span>}
              {issue.path && <small>{issue.path}</small>}
            </article>
          ))}
        </div>
      )}
      {scan.error && <span role="alert">{scan.error.message}</span>}
    </details>
  );
}
