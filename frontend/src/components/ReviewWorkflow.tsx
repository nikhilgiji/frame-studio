import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getStatistics } from "../services/statistics";

export function ReviewWorkflow({
  projectId,
  onOpenVideos,
}: {
  projectId: number;
  onOpenVideos: () => void;
}) {
  const statistics = useQuery({
    queryKey: ["statistics", projectId, {}],
    queryFn: ({ signal }) => getStatistics(projectId, {}, signal),
  });
  const data = statistics.data;
  const videosReady = (data?.total_videos ?? 0) > 0;
  const framesReady = (data?.total_frames ?? 0) > 0;
  const reviewed = data?.reviewed_frames ?? 0;
  const reviewComplete = reviewed >= 100;
  const exportComplete = (data?.export_jobs ?? 0) > 0;
  const nextStep = !videosReady
    ? "Import a video"
    : !framesReady
      ? "Extract frames"
      : !reviewComplete
        ? "Review frames"
        : !exportComplete
          ? "Export the dataset"
          : "Workflow complete";

  return (
    <section className="review-workflow" aria-labelledby="workflow-heading">
      <header>
        <div>
          <p className="eyebrow">Next step</p>
          <h3 id="workflow-heading">{nextStep}</h3>
        </div>
        {framesReady && !reviewComplete && (
          <Link
            className="button-link primary"
            to={`/projects/${projectId}/gallery?review_status=unreviewed`}
          >
            Continue review →
          </Link>
        )}
      </header>

      <ol className="workflow-steps">
        <li className={videosReady ? "done" : "current"}>
          <span>1</span>
          <div>
            <strong>Import</strong>
            <small>{videosReady ? "Video ready" : "Add a source video"}</small>
          </div>
          {!videosReady && <button onClick={onOpenVideos}>Open videos</button>}
        </li>
        <li className={framesReady ? "done" : videosReady ? "current" : ""}>
          <span>2</span>
          <div>
            <strong>Extract</strong>
            <small>
              {framesReady
                ? `${data?.total_frames.toLocaleString()} frames ready`
                : "Create frames from the video"}
            </small>
          </div>
          {videosReady && !framesReady && (
            <button onClick={onOpenVideos}>Open videos</button>
          )}
        </li>
        <li className={reviewComplete ? "done" : framesReady ? "current" : ""}>
          <span>3</span>
          <div>
            <strong>Review</strong>
            <small>{reviewed.toLocaleString()} of 100 reviewed</small>
          </div>
          {framesReady && !reviewComplete && (
            <Link
              to={`/projects/${projectId}/gallery?review_status=unreviewed`}
            >
              Start
            </Link>
          )}
        </li>
        <li
          className={exportComplete ? "done" : reviewComplete ? "current" : ""}
        >
          <span>4</span>
          <div>
            <strong>Export</strong>
            <small>
              {exportComplete ? "Dataset exported" : "Save your result"}
            </small>
          </div>
        </li>
      </ol>

      {framesReady && !reviewComplete && (
        <div className="review-instructions">
          <strong>How to review a frame</strong>
          <p>
            Open the gallery, double-click a frame, press <kbd>Space</kbd> to
            mark it reviewed, then press <kbd>→</kbd> for the next frame.
          </p>
          <progress max="100" value={Math.min(reviewed, 100)} />
          <span>{Math.min(reviewed, 100)}%</span>
        </div>
      )}
    </section>
  );
}
