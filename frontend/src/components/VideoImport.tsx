import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  useRef,
  useState,
  type ChangeEvent,
  type InputHTMLAttributes,
} from "react";

import { importVideos } from "../services/videos";
import type { VideoImportResult } from "../types/video";

interface FolderInputProps extends InputHTMLAttributes<HTMLInputElement> {
  webkitdirectory?: string;
  directory?: string;
}

export function VideoImport({ projectId }: { projectId: number }) {
  const queryClient = useQueryClient();
  const [files, setFiles] = useState<File[]>([]);
  const [result, setResult] = useState<VideoImportResult | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const folderProps: FolderInputProps = { webkitdirectory: "", directory: "" };
  const upload = useMutation({
    mutationFn: () => importVideos(projectId, files),
    onSuccess: (data) => {
      setResult(data);
      setFiles([]);
      if (fileInput.current) fileInput.current.value = "";
      void queryClient.invalidateQueries({ queryKey: ["videos", projectId] });
    },
  });

  function selected(event: ChangeEvent<HTMLInputElement>) {
    setFiles(Array.from(event.target.files ?? []));
    setResult(null);
  }

  return (
    <section className="video-import">
      <div>
        <h3>Import videos</h3>
        <p>Files are copied into this project for portability.</p>
      </div>
      <div className="import-controls">
        <label className="file-button">
          Choose files
          <input
            ref={fileInput}
            type="file"
            accept=".mp4,.avi,.mov,.mkv,.webm"
            multiple
            onChange={selected}
          />
        </label>
        <label className="file-button secondary">
          Choose folder
          <input
            type="file"
            accept=".mp4,.avi,.mov,.mkv,.webm"
            multiple
            {...folderProps}
            onChange={selected}
          />
        </label>
        <button
          disabled={!files.length || upload.isPending}
          onClick={() => upload.mutate()}
        >
          {upload.isPending
            ? "Importing…"
            : `Import ${files.length || ""} video${files.length === 1 ? "" : "s"}`}
        </button>
      </div>
      {upload.error && (
        <div role="alert" className="inline-error">
          {upload.error.message}
        </div>
      )}
      {result && (
        <div className="import-result" role="status">
          <span>{result.imported.length} imported</span>
          <span>{result.skipped.length} skipped</span>
          <span>{result.errors.length} failed</span>
          {[...result.skipped, ...result.errors].map((issue) => (
            <p key={`${issue.filename}-${issue.code}`}>
              <strong>{issue.filename}</strong>: {issue.message}
            </p>
          ))}
        </div>
      )}
    </section>
  );
}
