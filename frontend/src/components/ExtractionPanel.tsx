import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import {
  cancelExtraction,
  createExtraction,
  getExtraction,
} from "../services/extraction";
import type { ExtractionInput } from "../types/extraction";

export function ExtractionPanel({
  videoId,
  onClose,
}: {
  videoId: number;
  onClose: () => void;
}) {
  const [jobId, setJobId] = useState<number | null>(null);
  const [mode, setMode] = useState<ExtractionInput["mode"]>("every_n_frames");
  const [value, setValue] = useState(10);
  const [format, setFormat] =
    useState<ExtractionInput["output_format"]>("jpeg");
  const [quality, setQuality] = useState(90);
  const [width, setWidth] = useState("");
  const [height, setHeight] = useState("");
  const [overwrite, setOverwrite] = useState(false);
  const create = useMutation({
    mutationFn: (input: ExtractionInput) => createExtraction(videoId, input),
    onSuccess: (job) => setJobId(job.id),
  });
  const job = useQuery({
    queryKey: ["extraction", jobId],
    queryFn: ({ signal }) => getExtraction(jobId!, signal),
    enabled: jobId !== null,
    refetchInterval: (query) =>
      ["pending", "running", "cancelling"].includes(
        query.state.data?.status ?? "",
      )
        ? 500
        : false,
  });
  const cancel = useMutation({
    mutationFn: cancelExtraction,
    onSuccess: () => void job.refetch(),
  });
  const input: ExtractionInput = {
    mode,
    mode_value: value,
    output_format: format,
    jpeg_quality: quality,
    resize_width: width ? Number(width) : null,
    resize_height: height ? Number(height) : null,
    overwrite,
  };
  return (
    <div className="extraction-panel">
      {!jobId ? (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            create.mutate(input);
          }}
        >
          <label>
            Sampling
            <select
              value={mode}
              onChange={(e) =>
                setMode(e.target.value as ExtractionInput["mode"])
              }
            >
              <option value="every_n_frames">Every N frames</option>
              <option value="frames_per_second">Frames per second</option>
              <option value="every_n_seconds">Every N seconds</option>
            </select>
          </label>
          <label>
            Value
            <input
              type="number"
              min="0.01"
              step={mode === "every_n_frames" ? 1 : 0.01}
              value={value}
              onChange={(e) => setValue(Number(e.target.value))}
            />
          </label>
          <label>
            Format
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value as "jpeg" | "png")}
            >
              <option value="jpeg">JPEG</option>
              <option value="png">PNG</option>
            </select>
          </label>
          {format === "jpeg" && (
            <label>
              Quality
              <input
                type="number"
                min="1"
                max="100"
                value={quality}
                onChange={(e) => setQuality(Number(e.target.value))}
              />
            </label>
          )}
          <label>
            Max width
            <input
              type="number"
              value={width}
              onChange={(e) => setWidth(e.target.value)}
              placeholder="Original"
            />
          </label>
          <label>
            Max height
            <input
              type="number"
              value={height}
              onChange={(e) => setHeight(e.target.value)}
              placeholder="Original"
            />
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={overwrite}
              onChange={(e) => setOverwrite(e.target.checked)}
            />
            Overwrite existing
          </label>
          <button
            type="button"
            disabled={create.isPending || value <= 0}
            onClick={() => create.mutate(input)}
          >
            Start extraction
          </button>
          <button type="button" onClick={onClose}>
            Close
          </button>
          {create.error && <span role="alert">{create.error.message}</span>}
        </form>
      ) : (
        <div className="job-progress">
          <strong>{job.data?.status ?? "Starting"}</strong>
          <progress value={job.data?.progress ?? 0} max="100" />
          <span>
            {job.data?.processed_frames ?? 0} / {job.data?.total_frames ?? 0}{" "}
            frames
          </span>
          {job.data?.error_message && (
            <span role="alert">{job.data.error_message}</span>
          )}
          {["pending", "running"].includes(job.data?.status ?? "") && (
            <button onClick={() => cancel.mutate(jobId)}>Cancel</button>
          )}
          <button onClick={onClose}>Close</button>
        </div>
      )}
    </div>
  );
}
