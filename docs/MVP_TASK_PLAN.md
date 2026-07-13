# MVP task plan

Mirrors the vault note `CWS Internal Development Coordinator - MVP Implementation Plan`. One task per implementation burst; Hermes/Gregory verify after each. Update the checkbox and `docs/VERIFICATION_MATRIX.md` when a task passes.

## Phase 1 - Foundation

- [x] **T1 Starter repo** — modular-monolith skeleton, agent docs, Docker Compose Postgres, Alembic baseline, frontend scaffold. *(this commit)*
- [x] **T2 Migrations + reference data + auth scaffold** — native Postgres enums from `app/vocab.py`; people/projects/project_members; `app.authz` choke point (dev-auth login stub, real permission checks); append-only audit_events; bootstrap admin seed. Env vars are `IDC_`-prefixed; Postgres on dedicated port 5455.
- [x] **T3 Project CRUD + portfolio dashboard + project profile** — incl. `current_next_action`, link fields, `tech_stack_summary`, `data_as_of` display, audit events.
- [x] **T4 StatusEvent create/list + freshness computation** — stale flag (>14 days) on dashboard and profile.
- [x] **T5 Documentation matrix + RequiredDocProfile + deterministic gap list** — no AI.
- [x] **T6 Vault seed import (one-shot)** — loaded Health Fair, CWSCX, Pulse Awards and VAS with real statuses/doc inventories (both Pulse Awards and CWSCX included - see verification matrix); these records become the AI golden set.

**Phase 1 gate: met.** 4 pilot projects live with real data (exceeds the 3-project minimum); gap lists match real documentation inventory on disk; audit trail populated (`seed_import_run` x4 plus per-mutation events); zero AI involved.

## Phase 2 - Starter-pack generator

- [x] **T7 Deterministic templates + intake form** — file list frozen per FR-016; selection by project_type/classification.
- [x] **T8 AI tailoring + review workflow + zip export** — provider adapter; forbidden-data scans; human review before export; StarterPack + AIInteraction + audit records.

**Phase 2 gate: met.** Packs generated for 2 project types (verified: internal-web-app and operational-tool, both via real pilot projects); zero secrets in output (forbidden-data scan enforced pre-AI-call and on output). Real AI tailoring is now live — Gregory approved OpenRouter (`IDC_AI_PROVIDER=openrouter`, free-tier model) 2026-07-13 and a real generation against the CWS Pulse Awards pilot produced a grounded, non-generic README overview end to end (generate → review → export). "70%+ sections accepted with light edits" is a T10 golden-set/rubric measurement, not yet formally scored - only one manual real-provider run has happened so far.

## Phase 3 - AI structured summary

- [ ] **T9 Source-bundle builder + AI summary task** — audience-parameterised; structured JSON output; stale caveats; full AIInteraction logging.
- [ ] **T10 Golden set + rubric evaluation** — ~10 golden bundles from pilot records; 5-dimension rubric (grounded/accurate/complete/safe/useful); scored on every prompt version change.

**Phase 3 gate:** summaries cite source IDs; stale caveats fire; rubric pass; review state machine enforced.
