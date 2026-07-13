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
| T2 Migrations + authz + audit | 2026-07-13 | Claude (Fable 5) | Fresh Docker Postgres (port 5455) + `alembic upgrade head` clean (2 migrations); `pytest` 9/9 passed (authz role matrix, audit append-only contract, health); e2e: dev auth resolved bootstrap admin from live DB and appended audit event id 1. Env-var leak from other projects fixed via `IDC_` prefix. |
| T3 Project CRUD + portfolio dashboard + project profile | 2026-07-13 | Claude (Sonnet 5) | `alembic upgrade head` clean against live Docker Postgres (port 5455, no new migration needed - T2 schema already had all Project fields). `pytest` 17/17 passed (new `tests/test_registry.py`: slug generation/uniqueness, authz-scoped list for admin/manager/developer roles, 403/404 paths, audit events on create/update, slug immutability) using a real-DB fixture (`tests/conftest.py`, SAVEPOINT-per-test rollback). e2e: `POST/GET /api/projects` exercised via curl against a running `uvicorn` instance. Frontend: introduced Tailwind (DESIGN.md tokens), app shell, portfolio dashboard, project profile, create/edit form, dev-user switcher (X-User-Email stub). `npm run build` clean; browser-driven verification via Playwright (create → view → edit → blocked-status chip → portfolio refresh) at 1280px and 768px, zero console/page errors; fixed a table-layout bug (`table-fixed` + explicit column widths) so the "next action" column truncates instead of overflowing at 768px. Test project rows removed from the dev DB after verification. |

## Phase gates

| Gate | Criteria | Status |
|---|---|---|
| Phase 1 | 3 pilot projects live with real data; deterministic gap lists match reality; audit trail populated; no AI used | pending |
| Phase 2 | Packs for 2 project types; 70%+ sections accepted with light edits; zero secrets | pending |
| Phase 3 | Source-cited summaries; stale caveats fire; golden-set rubric pass; review state machine enforced | pending |
