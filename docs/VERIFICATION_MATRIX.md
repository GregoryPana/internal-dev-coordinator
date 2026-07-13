# Verification matrix

Every task records here what was verified, how, and by whom before it is called done. Agents append; Gregory/Hermes confirm.

## Standing checks (every task)

| Check | Command / method |
|---|---|
| Migrations clean on fresh DB | `docker compose up -d db` (fresh volume) then `alembic upgrade head` |
| Tests pass | `cd backend && pytest` |
| End-to-end exercise | Drive the affected API/UI flow, not only unit tests |
| No secrets | No secret-like strings in code, fixtures, generated output; `.env` not committed |
| Scope respected | Nothing from `docs/PROJECT_SCOPE.md` out-of-scope list introduced |

## Task verification log

| Task | Date | Verified by | Evidence |
|---|---|---|---|
| T1 Starter repo | 2026-07-13 | Claude (Fable 5) | Skeleton created; git history clean; no dependencies installed yet — build/run verification lands with T2. |

## Phase gates

| Gate | Criteria | Status |
|---|---|---|
| Phase 1 | 3 pilot projects live with real data; deterministic gap lists match reality; audit trail populated; no AI used | pending |
| Phase 2 | Packs for 2 project types; 70%+ sections accepted with light edits; zero secrets | pending |
| Phase 3 | Source-cited summaries; stale caveats fire; golden-set rubric pass; review state machine enforced | pending |
