# CWS Internal Development Coordinator

Internal development control plane for Cable & Wireless Seychelles (DTO): project registry, status evidence, documentation/`EXIT.md` matrix, Internal Dev Kit starter-pack generation, and one bounded AI summary task over structured fields.

> Data before AI. Workflow before automation. Integration before scale.

## What this is (MVP)

- **Project registry** — canonical list of internal dev projects: phase, status, owner, priority, `current_next_action`, blocker state, repo/env/docs links.
- **Status events** — the main update primitive (date, summary, completed work, next actions, blockers, verification notes). Freshness threshold: 14 days.
- **Documentation matrix** — artifact status per project, with required-doc profiles by project type and a deterministic gap list.
- **Starter-pack generator** — tailored Internal Dev Kit packs (deterministic templates + AI tailoring), human review, zip export.
- **One AI summary task** — audience-parameterised (developer/manager), structured fields only, source IDs + data-as-of + stale caveats, human review before official use.
- **Append-only audit log** and full `AIInteraction` logging.

## What this is NOT (MVP)

No work-item/task tracker (use GitHub Issues; `current_next_action` covers MVP). No formal Risk/Decision tables. No trainee view. No repo integration (links only). No vector RAG. No content-grounded gap reports. No autonomous coding/deployment. No productivity scoring.

## Architecture

**Modular monolith**: one FastAPI app, one PostgreSQL database, domain packages under `backend/app/` (`registry`, `status`, `docs_matrix`, `starterpack`, `ai`, `audit`, `authz`, `seed_import`). React/TypeScript frontend. Alembic migrations. AI provider adapter with prompts as versioned files. See `docs/ARCHITECTURE.md`.

## Quick start (local dev)

```bash
# database
docker compose up -d db

# backend
cd backend
python -m venv .venv && . .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp ../.env.example ../.env                          # then edit values
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# frontend
cd ../frontend
npm install
npm run dev
```

Dev auth is a **login stub only** — the role/permission model is real from day one. Entra/OIDC is the production target; the moment a second user logs in, Entra becomes mandatory.

## Documentation

| Doc | Purpose |
|---|---|
| `docs/PROJECT_SCOPE.md` | MVP cut line, out-of-scope list, phase plan |
| `docs/ARCHITECTURE.md` | Modular monolith layout, AI boundary, security model |
| `docs/DATA_MODEL.md` | Entities, controlled vocabularies, required-doc profiles |
| `docs/VERIFICATION_MATRIX.md` | What must be verified per task/phase |
| `docs/MVP_TASK_PLAN.md` | The 10-task build sequence with gates |
| `AGENTS.md` | Operating rules for AI coding agents (canonical) |
| `EXIT.md` | Handover/exit state of this project |

## Status

Phase 0 (product/architecture) closed 2026-07-13 after two Claude high-model reviews. Currently executing Phase 1, task 1-2 (starter repo + migrations). Owner: Gregory Panagary.
