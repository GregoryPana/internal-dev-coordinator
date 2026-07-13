import type { AIAudience, ArtifactType, HumanReviewStatus } from "./vocab";
import type {
  AIInteraction,
  DocArtifactUpsertPayload,
  DocMatrixEntry,
  IntakeFormValues,
  Project,
  ProjectFormValues,
  StarterPack,
  StarterPackPreview,
  StatusEvent,
  StatusEventPayload,
} from "./types";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, userEmail: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-User-Email": userEmail,
      ...init?.headers,
    },
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new ApiError(resp.status, body.detail || `Request failed (${resp.status})`);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json() as Promise<T>;
}

export function listProjects(userEmail: string): Promise<Project[]> {
  return request("/api/projects", userEmail);
}

export function getProject(userEmail: string, id: number): Promise<Project> {
  return request(`/api/projects/${id}`, userEmail);
}

export function createProject(userEmail: string, data: ProjectFormValues): Promise<Project> {
  return request("/api/projects", userEmail, { method: "POST", body: JSON.stringify(data) });
}

export function updateProject(
  userEmail: string,
  id: number,
  data: Partial<ProjectFormValues>
): Promise<Project> {
  return request(`/api/projects/${id}`, userEmail, { method: "PATCH", body: JSON.stringify(data) });
}

export function listStatusEvents(userEmail: string, projectId: number): Promise<StatusEvent[]> {
  return request(`/api/projects/${projectId}/status-events`, userEmail);
}

export function createStatusEvent(
  userEmail: string,
  projectId: number,
  data: StatusEventPayload
): Promise<StatusEvent> {
  return request(`/api/projects/${projectId}/status-events`, userEmail, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getDocumentationMatrix(userEmail: string, projectId: number): Promise<DocMatrixEntry[]> {
  return request(`/api/projects/${projectId}/documentation`, userEmail);
}

export function upsertDocumentationArtifact(
  userEmail: string,
  projectId: number,
  artifactType: ArtifactType,
  data: DocArtifactUpsertPayload
): Promise<DocMatrixEntry> {
  return request(`/api/projects/${projectId}/documentation/${artifactType}`, userEmail, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function generateStarterPackPreview(
  userEmail: string,
  projectId: number,
  intake: IntakeFormValues
): Promise<StarterPackPreview> {
  return request(`/api/projects/${projectId}/starter-pack/preview`, userEmail, {
    method: "POST",
    body: JSON.stringify(intake),
  });
}

export function generateStarterPack(
  userEmail: string,
  projectId: number,
  intake: IntakeFormValues
): Promise<StarterPack> {
  return request(`/api/projects/${projectId}/starter-pack/generate`, userEmail, {
    method: "POST",
    body: JSON.stringify(intake),
  });
}

export function reviewStarterPack(
  userEmail: string,
  projectId: number,
  packId: number,
  decision: Extract<HumanReviewStatus, "reviewed" | "rejected">
): Promise<StarterPack> {
  return request(`/api/projects/${projectId}/starter-pack/${packId}/review`, userEmail, {
    method: "POST",
    body: JSON.stringify({ decision }),
  });
}

export async function exportStarterPack(
  userEmail: string,
  projectId: number,
  packId: number
): Promise<Blob> {
  const resp = await fetch(`/api/projects/${projectId}/starter-pack/${packId}/export`, {
    headers: { "X-User-Email": userEmail },
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new ApiError(resp.status, body.detail || `Request failed (${resp.status})`);
  }
  return resp.blob();
}

export function generateSummary(
  userEmail: string,
  projectId: number,
  audience: AIAudience
): Promise<AIInteraction> {
  return request(`/api/projects/${projectId}/ai/summary`, userEmail, {
    method: "POST",
    body: JSON.stringify({ audience }),
  });
}

export function listSummaries(userEmail: string, projectId: number): Promise<AIInteraction[]> {
  return request(`/api/projects/${projectId}/ai/summaries`, userEmail);
}

export function reviewSummary(
  userEmail: string,
  projectId: number,
  interactionId: number,
  decision: Extract<HumanReviewStatus, "reviewed" | "rejected">
): Promise<AIInteraction> {
  return request(`/api/projects/${projectId}/ai/summaries/${interactionId}/review`, userEmail, {
    method: "POST",
    body: JSON.stringify({ decision }),
  });
}
