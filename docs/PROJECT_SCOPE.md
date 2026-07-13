# Project scope - MVP cut line

Confirmed by Gregory 2026-07-13 after two Claude high-model Phase 0 reviews. Source of truth for scope disputes: the Phase 0 Product and Architecture Specification in the Hermes vault (`04 - Projects/CWS DTO/`).

## In scope (MVP = Phases 1-3)

- Project registry with controlled phase/status vocabularies, owners, priority, `current_next_action`, blocker visibility.
- Repo/environment/docs **link fields only** — no repo integration.
- Status events as the main update primitive; 14-day freshness threshold with `data_as_of` display everywhere.
- Documentation artifact matrix + required-doc profiles by project type + **deterministic** gap list.
- Internal Dev Kit starter-pack generator: intake form, deterministic templates, AI tailoring, human review, zip export.
- One audience-parameterised AI project summary (developer/manager) from structured fields, with source IDs, stale caveats, structured output validation and review workflow.
- Append-only audit events; full AIInteraction logging.
- One-shot vault/CSV seed import (pilot projects: Health Fair, Pulse Awards or CWSCX, VAS).

## Out of scope (MVP) — do not build

- WorkItem/task tracking tables (GitHub Issues later; `current_next_action` + blockers cover MVP).
- Formal Risk/Decision tables (captured in status-event notes until usage justifies tables).
- Trainee role views; separate manager view implementations (shared views, audience-appropriate content).
- Repo/GitHub/GitLab integration of any kind (read integration is Phase 4).
- Content-grounded documentation/EXIT gap reports (Phase 5, after repo read exists).
- Vector RAG / embeddings / semantic search.
- Prompt caching.
- Autonomous coding, deployment, vulnerability remediation, or any write action to external systems.
- Individual productivity scoring/ranking.
- Live vault sync (seed import is one-shot).

## Phase map

| Phase | Content |
|---|---|
| 1 | Foundation: repo, migrations/vocab, auth scaffold, project CRUD, status events, docs matrix, seed import |
| 2 | Starter-pack generator |
| 3 | AI summary task + golden-set evaluation |
| 4 | GitHub read integration (later) |
| 5 | Content-grounded doc reports (later) |
| 6-8 | Manager/KPI views, quality coordination, bounded agentic actions (much later) |
