# Data model - MVP baseline

Entities and controlled vocabularies for the MVP. Vocabularies are implemented in `backend/app/vocab.py` and seeded via Alembic migration; changing them is a migration + docs update.

## Entities

| Entity | Key fields |
|---|---|
| Person | id, name, email, role_type, department, active |
| Project | id, slug, name, description, business_purpose, project_type, classification, phase, status, priority, owner_id, business_owner, current_next_action, repo_url, environment_url, docs_url, tech_stack_summary, data_as_of, created_at, updated_at |
| ProjectMember | project_id, person_id, role, permissions |
| StatusEvent | id, project_id, author_id, event_date, summary, completed_work, next_actions, blockers, verification_notes, created_at |
| RequiredDocProfile | id, project_type, artifact_type, required, notes |
| DocumentationArtifact | id, project_id, artifact_type, title, required, status, source_path, owner_id, last_reviewed_at, staleness_checked_at, notes |
| StarterPack | id, project_id, intake_json, generated_files_json, export_path, status, reviewed_by, created_at |
| AIInteraction | id, project_id, task_type, audience, prompt_id, prompt_version, source_ids_json, input_bundle_hash, model_provider, model_name, output_text, output_json, input_tokens, output_tokens, latency_ms, error_category, estimated_cost, validation_status, human_review_status, created_at |
| AuditEvent | id, actor_id, project_id, action_type, object_type, object_id, metadata_json, created_at — **append-only** |
| Job | id, job_type, status, payload_json, result_json, error_category, created_by, created_at, started_at, completed_at |

Deferred entities (do not create): WorkItem, Risk, Decision, Milestone, Repository, RepoSnapshot, Environment, VerificationRun, VulnerabilityFinding, KPIEvidenceItem, PromptTemplate table.

## Controlled vocabularies

| Vocabulary | Values |
|---|---|
| Project phase | concept, discovery, build, pilot, live, handover, retired |
| Project status | active, blocked, paused, complete, cancelled |
| Priority | high, medium, low |
| project_type | internal-web-app, operational-tool, prototype |
| classification | one-off, reusable, platform |
| artifact_type | user_guide, admin_guide, developer_guide, agent_guide, support_runbook, deployment_guide, verification_matrix, exit_md |
| artifact status | missing, draft, current, stale, approved, retired |
| Role | admin, developer_project_owner, trainee, manager, end_user, auditor, ai_service_account |
| AI task_type | project_summary, starter_pack_tailoring |
| AI audience | developer, manager |
| validation_status | passed, failed_schema, failed_missing_sources, failed_forbidden_data |
| human_review_status | generated, reviewed, exported, rejected |
| job_type | ai_run, seed_import, starter_pack_generation |
| job status | queued, running, succeeded, failed |
| error_category | provider_unavailable, timeout, rate_limited, context_too_large, malformed_output, validation_failed, forbidden_data_detected, access_denied, budget_exceeded, internal_error |
| audit action_type | project_created, project_updated, status_event_created, doc_artifact_created, doc_artifact_updated, starter_pack_generated, starter_pack_reviewed, starter_pack_exported, ai_run_created, ai_output_reviewed, seed_import_run, member_added, member_removed |
| audit object_type | project, status_event, documentation_artifact, starter_pack, ai_interaction, project_member, job |

Note: `trainee` and `end_user` role values exist from day one even though their views are deferred — the permission model must never need a schema change to add them.

## Required documentation profiles

| artifact_type | internal-web-app | operational-tool | prototype |
|---|---|---|---|
| user_guide | Required | - | - |
| admin_guide | Required | - | - |
| developer_guide | Required | Required | - |
| agent_guide | Required | Required | Required |
| support_runbook | Required | Required | - |
| deployment_guide | Required | Required | - |
| verification_matrix | Required | Required | - |
| exit_md | Required | Required | Required |

## Configuration constants

| Constant | Value |
|---|---|
| Freshness threshold | 14 days |
| Starter-pack export | zip download after review |
| Seed import | one-shot CSV/JSON command |
