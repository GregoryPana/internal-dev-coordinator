import type {
  AIAudience,
  ArtifactStatus,
  ArtifactType,
  AuditActionType,
  AuditObjectType,
  Classification,
  HumanReviewStatus,
  Priority,
  ProjectPhase,
  ProjectStatus,
  ProjectType,
  ValidationStatus,
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
  date_commenced: string | null;
  expected_finish_date: string | null;
  percent_complete: number | null;
  uses_process_automation: boolean;
  uses_ai: boolean;
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

export interface SummaryOutput {
  summary: string;
  assumptions: string[];
  gaps: string[];
  recommended_next_actions: string[];
  requires_human_review: boolean;
  confidence: number;
}

export interface AIInteraction {
  id: number;
  project_id: number;
  task_type: string;
  audience: AIAudience | null;
  prompt_id: string;
  prompt_version: number;
  source_ids_json: Record<string, unknown>;
  model_provider: string;
  model_name: string;
  output_json: SummaryOutput | null;
  input_tokens: number | null;
  output_tokens: number | null;
  latency_ms: number | null;
  error_category: string | null;
  validation_status: ValidationStatus;
  human_review_status: HumanReviewStatus;
  created_at: string;
}

export interface RepoLastCommit {
  sha: string;
  message: string;
  author: string | null;
  committed_at: string | null;
}

export interface RepoSignals {
  repo_full_name: string;
  default_branch: string;
  pushed_at: string | null;
  last_commit: RepoLastCommit | null;
  open_pr_count: number;
  open_issue_count: number;
  fetched_at: string;
}

export interface AuditEvent {
  id: number;
  actor_id: number | null;
  actor_name: string | null;
  actor_email: string | null;
  project_id: number | null;
  action_type: AuditActionType;
  object_type: AuditObjectType;
  object_id: number | null;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
}

export interface AuditEventPage {
  items: AuditEvent[];
  total: number;
  limit: number;
  offset: number;
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
  | "date_commenced"
  | "expected_finish_date"
  | "percent_complete"
  | "uses_process_automation"
  | "uses_ai"
>;

export interface GitHubIntegrationStatus {
  provider: "github";
  enabled: boolean;
  source: "app" | "env";
  credential_set: boolean;
  api_base: string;
  updated_at: string | null;
  secret_key_configured: boolean;
}

export interface IntegrationTestResult {
  ok: boolean;
  detail: string;
  authenticated?: boolean;
  rate_limit_remaining?: number | null;
}

export interface AppConfig {
  status: string;
  app: string;
  env: string;
  edition: "custom" | "product";
}
