# Agent instructions - CWS Internal Development Coordinator

Canonical operating rules for all AI coding agents (Claude Code, OpenCode, Codex, etc.) working in this repository. `CLAUDE.md` and `OPENCODE.md` point here.

## Read first

1. `docs/PROJECT_SCOPE.md` — the MVP cut line. Do not implement anything on the out-of-scope list.
2. `docs/MVP_TASK_PLAN.md` — the current task and its acceptance criteria.
3. `docs/DATA_MODEL.md` — entities and controlled vocabularies. Never invent enum values.
4. `docs/VERIFICATION_MATRIX.md` — what to verify before calling a task done.
5. Before substantial frontend/UI work: `docs/AGENT_DESIGN_SKILLS.md` and `DESIGN.md` — the project design-system and UI quality gate.

## Hard rules

- **Modular monolith.** One FastAPI app, one PostgreSQL database. Domain packages under `backend/app/`. Do NOT create separate services, extra databases, message brokers, Celery/Redis, or a vector DB. Async work uses the Postgres-backed `jobs` table pattern.
- **Controlled vocabularies are law.** All enums come from `backend/app/vocab.py` (mirrors `docs/DATA_MODEL.md`). Adding/changing a value is an Alembic migration plus a docs update, never an inline string.
- **Single authorization choke point.** Every permission decision goes through `app.authz`. No inline permission checks in routers/services. The AI source-bundle builder must enforce the requesting user's access.
- **Audit is append-only.** No UPDATE or DELETE paths on `audit_events`, ever.
- **AI boundary.** AI tasks in MVP: `project_summary` and `starter_pack_tailoring` only. Prompts are versioned files in `backend/app/ai/prompts/` with a version header. Every run creates an `AIInteraction` record (prompt version, source IDs, tokens, latency, cost, validation + review status). AI output is never official until human-reviewed. No prompt caching, no embeddings.
- **Prompt/evaluation continuation.** Before changing the summary prompts or golden-set harness after prompt v2, read `docs/eval/HERMES_EVALUATION_V2_2026-07-14.md`. It preserves the advisory case scores, exact failure evidence, known pre-screen false positives/negatives, immutable-artifact requirement and ordered continuation brief. Gregory remains the formal scorer; do not overwrite the existing v2 evidence or represent advisory scores as his completed rubric.
- **Forbidden data.** Never send or store secrets, `.env` content, tokens, passwords, private keys or unnecessary PII. Scan user-entered free text, AI input bundles and AI outputs for secret-like data.
- **Freshness.** `data_as_of` is displayed on project profiles and AI outputs; stale caveat fires past 14 days.
- **Scope discipline.** If a change implies WorkItems, risk/decision tables, trainee views, repo integration, content-grounded reports or any write action to external systems — stop and flag it. These are deliberately deferred, not forgotten.
- **No deployment actions.** Do not push, deploy, or touch external systems unless Gregory explicitly asks.

## Conventions

- Backend: FastAPI + SQLAlchemy 2.x + Alembic; Python 3.12; type hints throughout; `pytest` for tests.
- Frontend: React + TypeScript + Vite; keep it plain — no state-management libraries until needed.
- UI/design: follow `DESIGN.md` and `docs/AGENT_DESIGN_SKILLS.md`. Default direction is clean/professional CWS internal SaaS control plane: evidence-led, light-first, status/freshness/review states visible, restrained motion. Use shadcn-style component discipline if/when Tailwind/shadcn is introduced.
- Migrations: one migration per task; descriptive slugs; reference data seeded via migration.
- Commits: conventional prefixes (`feat:`, `fix:`, `docs:`, `chore:`); small, task-scoped commits; never commit `.env`.
- Every completed task updates `docs/VERIFICATION_MATRIX.md` with what was verified and how.

## Verification before "done"

- `alembic upgrade head` runs clean on a fresh database.
- `pytest` passes.
- The affected flow is exercised end-to-end (API call or UI), not just unit-tested.
- No secret-like strings in code, fixtures or generated output.
- UI work also requires `cd frontend && npm run build`, browser inspection of changed routes, console check, responsive review, and a short scorecard against `DESIGN.md`.
