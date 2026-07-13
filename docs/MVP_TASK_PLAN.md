# MVP task plan

Mirrors the vault note `CWS Internal Development Coordinator - MVP Implementation Plan`. One task per implementation burst; Hermes/Gregory verify after each. Update the checkbox and `docs/VERIFICATION_MATRIX.md` when a task passes.

## Phase 1 - Foundation

- [x] **T1 Starter repo** — modular-monolith skeleton, agent docs, Docker Compose Postgres, Alembic baseline, frontend scaffold. *(this commit)*
- [ ] **T2 Migrations + reference data + auth scaffold** — vocab enums/reference tables; people/projects/project_members; `app.authz` choke point (dev-auth login stub, real permission checks); append-only audit_events.
- [ ] **T3 Project CRUD + portfolio dashboard + project profile** — incl. `current_next_action`, link fields, `tech_stack_summary`, `data_as_of` display, audit events.
- [ ] **T4 StatusEvent create/list + freshness computation** — stale flag (>14 days) on dashboard and profile.
- [ ] **T5 Documentation matrix + RequiredDocProfile + deterministic gap list** — no AI.
- [ ] **T6 Vault seed import (one-shot)** — load Health Fair, Pulse/CWSCX, VAS with real statuses/doc inventories; these records become the AI golden set.

**Phase 1 gate:** 3 pilot projects live with real data; gap lists match documentation reality; audit trail populated; zero AI involved.

## Phase 2 - Starter-pack generator

- [ ] **T7 Deterministic templates + intake form** — file list frozen per FR-016; selection by project_type/classification.
- [ ] **T8 AI tailoring + review workflow + zip export** — provider adapter; forbidden-data scans; human review before export; StarterPack + AIInteraction + audit records.

**Phase 2 gate:** packs for 2 project types; 70%+ sections accepted with light edits; zero secrets in output.

## Phase 3 - AI structured summary

- [ ] **T9 Source-bundle builder + AI summary task** — audience-parameterised; structured JSON output; stale caveats; full AIInteraction logging.
- [ ] **T10 Golden set + rubric evaluation** — ~10 golden bundles from pilot records; 5-dimension rubric (grounded/accurate/complete/safe/useful); scored on every prompt version change.

**Phase 3 gate:** summaries cite source IDs; stale caveats fire; rubric pass; review state machine enforced.
