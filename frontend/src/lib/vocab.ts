// Controlled vocabularies - mirrors backend/app/vocab.py and docs/DATA_MODEL.md.
// Never invent values here; a new value requires a backend migration + docs update first.

export const PROJECT_PHASES = [
  "concept",
  "discovery",
  "build",
  "pilot",
  "live",
  "handover",
  "retired",
] as const;
export type ProjectPhase = (typeof PROJECT_PHASES)[number];

export const PROJECT_STATUSES = ["active", "blocked", "paused", "complete", "cancelled"] as const;
export type ProjectStatus = (typeof PROJECT_STATUSES)[number];

export const PRIORITIES = ["high", "medium", "low"] as const;
export type Priority = (typeof PRIORITIES)[number];

export const PROJECT_TYPES = ["internal-web-app", "operational-tool", "prototype"] as const;
export type ProjectType = (typeof PROJECT_TYPES)[number];

export const CLASSIFICATIONS = ["one-off", "reusable", "platform"] as const;
export type Classification = (typeof CLASSIFICATIONS)[number];

export const PROJECT_PHASE_LABELS: Record<ProjectPhase, string> = {
  concept: "Concept",
  discovery: "Discovery",
  build: "Build",
  pilot: "Pilot",
  live: "Live",
  handover: "Handover",
  retired: "Retired",
};

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  active: "Active",
  blocked: "Blocked",
  paused: "Paused",
  complete: "Complete",
  cancelled: "Cancelled",
};

export const PRIORITY_LABELS: Record<Priority, string> = {
  high: "High",
  medium: "Medium",
  low: "Low",
};

export const PROJECT_TYPE_LABELS: Record<ProjectType, string> = {
  "internal-web-app": "Internal web app",
  "operational-tool": "Operational tool",
  prototype: "Prototype",
};

export const CLASSIFICATION_LABELS: Record<Classification, string> = {
  "one-off": "One-off",
  reusable: "Reusable",
  platform: "Platform",
};

// Visual status-chip tone per DESIGN.md section 6 ("Status chips").
export type ChipTone = "success" | "warning" | "danger" | "neutral";

export const PROJECT_STATUS_TONE: Record<ProjectStatus, ChipTone> = {
  active: "success",
  blocked: "danger",
  paused: "neutral",
  complete: "success",
  cancelled: "neutral",
};

export const ARTIFACT_TYPES = [
  "user_guide",
  "admin_guide",
  "developer_guide",
  "agent_guide",
  "support_runbook",
  "deployment_guide",
  "verification_matrix",
  "exit_md",
] as const;
export type ArtifactType = (typeof ARTIFACT_TYPES)[number];

export const ARTIFACT_STATUSES = ["missing", "draft", "current", "stale", "approved", "retired"] as const;
export type ArtifactStatus = (typeof ARTIFACT_STATUSES)[number];

export const ARTIFACT_TYPE_LABELS: Record<ArtifactType, string> = {
  user_guide: "User guide",
  admin_guide: "Admin guide",
  developer_guide: "Developer guide",
  agent_guide: "Agent guide",
  support_runbook: "Support runbook",
  deployment_guide: "Deployment guide",
  verification_matrix: "Verification matrix",
  exit_md: "EXIT.md",
};

export const ARTIFACT_STATUS_LABELS: Record<ArtifactStatus, string> = {
  missing: "Missing",
  draft: "Draft",
  current: "Current",
  stale: "Stale",
  approved: "Approved",
  retired: "Retired",
};

export const ARTIFACT_STATUS_TONE: Record<ArtifactStatus, ChipTone> = {
  missing: "neutral",
  draft: "neutral",
  current: "success",
  stale: "warning",
  approved: "success",
  retired: "neutral",
};

export const HUMAN_REVIEW_STATUSES = ["generated", "reviewed", "exported", "rejected"] as const;
export type HumanReviewStatus = (typeof HUMAN_REVIEW_STATUSES)[number];

export const HUMAN_REVIEW_STATUS_LABELS: Record<HumanReviewStatus, string> = {
  generated: "Awaiting review",
  reviewed: "Reviewed",
  exported: "Exported",
  rejected: "Rejected",
};

export const HUMAN_REVIEW_STATUS_TONE: Record<HumanReviewStatus, ChipTone> = {
  generated: "warning",
  reviewed: "success",
  exported: "success",
  rejected: "danger",
};

export const AI_AUDIENCES = ["developer", "manager"] as const;
export type AIAudience = (typeof AI_AUDIENCES)[number];

export const AI_AUDIENCE_LABELS: Record<AIAudience, string> = {
  developer: "Developer",
  manager: "Manager",
};

export const VALIDATION_STATUSES = [
  "passed",
  "failed_schema",
  "failed_missing_sources",
  "failed_forbidden_data",
] as const;
export type ValidationStatus = (typeof VALIDATION_STATUSES)[number];

export const VALIDATION_STATUS_LABELS: Record<ValidationStatus, string> = {
  passed: "Passed",
  failed_schema: "Failed - malformed output",
  failed_missing_sources: "Failed - missing sources",
  failed_forbidden_data: "Failed - forbidden data detected",
};
