# Claude Code instructions

Follow `AGENTS.md` (canonical agent rules) and the read-first list there.

Claude-specific notes:

- Work one task at a time from `docs/MVP_TASK_PLAN.md`; confirm the task's acceptance criteria before starting the next.
- Prefer editing existing modules over creating new top-level packages — the package layout in `backend/app/` is fixed for MVP.
- Before substantial frontend/UI work, read `docs/AGENT_DESIGN_SKILLS.md` and `DESIGN.md`; use the clean/professional CWS internal SaaS control-plane design system.
- Run `pytest` and `alembic upgrade head` against a fresh Docker Postgres before declaring a task complete.
- Do not commit or push unless Gregory asks. Never touch `main` history.
