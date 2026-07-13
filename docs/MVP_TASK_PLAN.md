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

- [x] **T9 Source-bundle builder + AI summary task** — audience-parameterised; structured JSON output; stale caveats; full AIInteraction logging.
- [ ] **T10 Golden set + rubric evaluation** — 8 golden bundles (4 real pilots × developer/manager audience - "~10" per the vault plan, but only 4 real pilot projects exist and padding with fabricated duplicates was rejected); 5-dimension rubric (grounded/accurate/complete/safe/useful) defined in `docs/eval/RUBRIC.md`; harness built (`python -m app.ai.eval.run_golden_set`) and a real report generated (`docs/eval/golden_set_report_v1_2026-07-13.md`, 7/8 bundles produced real, grounded, audience-differentiated output; 1/8 failed cleanly on a real model hiccup). **Not checked off**: the rubric scoring itself is explicitly Gregory's call per the vault plan ("Gregory scores on every prompt version change") - not something an agent should self-score. Awaiting Gregory's scores in the report file.

**Phase 3 gate: partially met.** Summaries cite source IDs (`source_ids_json`, deterministically built from the bundle, not the model's self-report); stale caveats fire (enforced deterministically, not just prompted); review state machine (generated → reviewed/rejected) enforced. Live-verified against the real VAS Network Check pilot (developer and manager audience) - correctly grounded, real documentation gaps cited, no hallucinated facts observed. Rubric pass criterion is open until Gregory scores `docs/eval/golden_set_report_v1_2026-07-13.md`.
