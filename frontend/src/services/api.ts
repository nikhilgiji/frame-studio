const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export interface HealthResponse {
  status: "ok";
}

export interface ApiErrorBody {
  data: null;
  error: { code: string; message: string };
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly code = "API_ERROR",
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!(init?.body instanceof FormData))
    headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  });
  if (!response.ok) {
    const body = (await response
      .json()
      .catch(() => null)) as ApiErrorBody | null;
    throw new ApiError(
      response.status,
      body?.error.message ?? "The request failed.",
      body?.error.code,
    );
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  try {
    return await apiRequest<HealthResponse>("/health", { signal });
  } catch (error) {
    if (error instanceof ApiError)
      throw new ApiError(error.status, "The local API is unavailable.");
    throw error;
  }
}
