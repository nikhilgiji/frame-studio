import { apiRequest } from "./api";
import type {
  ProjectEnvelope,
  ProjectInput,
  ProjectListEnvelope,
} from "../types/project";

export async function listProjects(signal?: AbortSignal) {
  return (await apiRequest<ProjectListEnvelope>("/projects", { signal })).data;
}

export async function getProject(id: number, signal?: AbortSignal) {
  return (await apiRequest<ProjectEnvelope>(`/projects/${id}`, { signal }))
    .data;
}

export async function createProject(input: ProjectInput) {
  return (
    await apiRequest<ProjectEnvelope>("/projects", {
      method: "POST",
      body: JSON.stringify(input),
    })
  ).data;
}

export async function updateProject(id: number, input: ProjectInput) {
  return (
    await apiRequest<ProjectEnvelope>(`/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(input),
    })
  ).data;
}

export async function deleteProject(id: number) {
  await apiRequest<void>(`/projects/${id}`, { method: "DELETE" });
}
