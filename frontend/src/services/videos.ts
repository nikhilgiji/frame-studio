import { apiRequest } from "./api";
import type { Video, VideoImportResult } from "../types/video";

export async function listVideos(projectId: number, signal?: AbortSignal) {
  return (
    await apiRequest<{ data: Video[] }>(`/projects/${projectId}/videos`, {
      signal,
    })
  ).data;
}

export async function importVideos(projectId: number, files: File[]) {
  const form = new FormData();
  files.forEach((file) =>
    form.append("files", file, file.webkitRelativePath || file.name),
  );
  return (
    await apiRequest<{ data: VideoImportResult }>(
      `/projects/${projectId}/videos/import`,
      {
        method: "POST",
        body: form,
      },
    )
  ).data;
}

export async function deleteVideo(videoId: number) {
  await apiRequest<void>(`/videos/${videoId}`, { method: "DELETE" });
}
