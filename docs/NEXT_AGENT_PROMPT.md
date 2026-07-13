# Next-agent prompt

Paste this (or an adapted version) into a fresh Claude Code / OpenCode session opened in this repository. Update the task line as tasks complete.

---

You are working on the CWS Internal Development Coordinator. Before doing anything:

1. Read `AGENTS.md` — hard rules (modular monolith, controlled vocabularies in `backend/app/vocab.py`, single `app.authz` choke point, append-only audit, scope discipline).
2. Read `docs/PROJECT_SCOPE.md` — the MVP cut line. Anything on the out-of-scope list is forbidden; flag it instead of building it.
3. Read `docs/MVP_TASK_PLAN.md` — find the first unchecked task; that is your only job this session.
4. Read `docs/DATA_MODEL.md` and skim `docs/ARCHITECTURE.md`.

Then implement the current task only:

- Follow the existing code patterns (see `backend/app/registry/models.py`, `backend/app/authz/service.py`, `backend/app/audit/service.py`).
- Environment: `docker compose up -d db` (Postgres on port 5455), backend venv at `backend/.venv`, env vars are `IDC_`-prefixed (see `.env.example`).
- Every mutation records an audit event via `app.audit.service.record()`; every permission decision goes through `app.authz.service`.
- Verify before done: `alembic upgrade head` clean on a fresh DB, `pytest` green, and exercise the affected flow end-to-end (API call or UI).
- Update `docs/MVP_TASK_PLAN.md` (check the task) and append a row to `docs/VERIFICATION_MATRIX.md` with evidence.
- Commit with a conventional message; do not push unless Gregory asks.

Stop when the task's acceptance criteria are met. Do not start the next task.
