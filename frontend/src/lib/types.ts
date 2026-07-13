import type {
  ArtifactStatus,
  ArtifactType,
  Classification,
  HumanReviewStatus,
  Priority,
  ProjectPhase,
  ProjectStatus,
  ProjectType,
} from "./vocab";

export interface ProjectOwner {
  id: number;
  name: string;
  email: string;
}

export interface Project {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  business_purpose: string | null;
  project_type: ProjectType;
  classification: Classification;
  phase: ProjectPhase;
  status: ProjectStatus;
  priority: Priority;
  owner_id: number | null;
  owner: ProjectOwner | null;
  business_owner: string | null;
  current_next_action: string | null;
  repo_url: string | null;
  environment_url: string | null;
  docs_url: string | null;
  tech_stack_summary: string | null;
  data_as_of: string | null;
  is_stale: boolean;
  created_at: string;
  updated_at: string;
}

export interface StatusEventAuthor {
  id: number;
  name: string;
  email: string;
}

export interface StatusEvent {
  id: number;
  project_id: number;
  author: StatusEventAuthor;
  event_date: string;
  summary: string;
  completed_work: string | null;
  next_actions: string | null;
  blockers: string | null;
  verification_notes: string | null;
  created_at: string;
}

export interface StatusEventFormValues {
  event_date: string;
  summary: string;
  completed_work: string;
  next_actions: string;
  blockers: string;
  verification_notes: string;
}

export interface StatusEventPayload {
  event_date: string;
  summary: string;
  completed_work: string | null;
  next_actions: string | null;
  blockers: string | null;
  verification_notes: string | null;
}

export interface DocMatrixOwner {
  id: number;
  name: string;
  email: string;
}

export interface DocMatrixEntry {
  artifact_type: ArtifactType;
  required: boolean;
  status: ArtifactStatus;
  is_gap: boolean;
  title: string | null;
  source_path: string | null;
  owner: DocMatrixOwner | null;
  last_reviewed_at: string | null;
  staleness_checked_at: string | null;
  notes: string | null;
}

export interface DocArtifactUpsertPayload {
  title: string | null;
  status: ArtifactStatus;
  source_path: string | null;
  owner_id: number | null;
  last_reviewed_at: string | null;
  notes: string | null;
}

export interface IntakeFormValues {
  users: string;
  workflow: string;
  data_sensitivity: string;
  integrations: string;
  deployment_target: string;
  notes: string;
}

export interface GeneratedFile {
  path: string;
  content: string;
}

export interface StarterPackPreview {
  project_id: number;
  files: GeneratedFile[];
}

export interface StarterPackReviewer {
  id: number;
  name: string;
  email: string;
}

export interface StarterPack {
  id: number;
  project_id: number;
  intake: IntakeFormValues;
  files: GeneratedFile[];
  status: HumanReviewStatus;
  reviewer: StarterPackReviewer | null;
  export_path: string | null;
  created_at: string;
}

export type ProjectFormValues = Pick<
  Project,
  | "name"
  | "description"
  | "business_purpose"
  | "project_type"
  | "classification"
  | "phase"
  | "status"
  | "priority"
  | "business_owner"
  | "current_next_action"
  | "repo_url"
  | "environment_url"
  | "docs_url"
  | "tech_stack_summary"
>;
