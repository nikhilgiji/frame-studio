import { apiRequest } from "./api";
import type { ExtractionInput, ExtractionJob } from "../types/extraction";

export async function createExtraction(
  videoId: number,
  input: ExtractionInput,
) {
  return (
    await apiRequest<{ data: ExtractionJob }>(
      `/videos/${videoId}/extraction-jobs`,
      { method: "POST", body: JSON.stringify(input) },
    )
  ).data;
}
export async function getExtraction(id: number, signal?: AbortSignal) {
  return (
    await apiRequest<{ data: ExtractionJob }>(`/extraction-jobs/${id}`, {
      signal,
    })
  ).data;
}
export async function cancelExtraction(id: number) {
  return (
    await apiRequest<{ data: ExtractionJob }>(`/extraction-jobs/${id}/cancel`, {
      method: "POST",
    })
  ).data;
}
