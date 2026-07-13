# Seed import (T6) - what to bring from the Hermes vault

This is a **one-shot** command (`python -m app.seed_import.cli --file <path>`)
that loads real pilot-project records into the database. It never invents
data - every field comes from the JSON file you provide. The importer is
safe to re-run against a corrected file: it upserts people by email,
projects by slug, documentation artifacts by (project, artifact_type), and
skips status events that already exist with the same (project, event_date,
summary) rather than duplicating them.

## What to export from the vault

For each of the 3 pilot projects (Health Fair, Pulse Awards or CWSCX, VAS),
pull the following from the Hermes vault note(s) and fill in
`templates/pilot_projects.template.json` (copy it somewhere outside
version control first, e.g. `backend/seed_data/pilot_projects.json` -
it may contain real internal project details):

1. **Project identity** - real name, one-line description, business
   purpose.
2. **Classification fields** - which of these apply, from the controlled
   vocabularies in `docs/DATA_MODEL.md` / `backend/app/vocab.py`:
   - `project_type`: `internal-web-app` | `operational-tool` | `prototype`
   - `classification`: `one-off` | `reusable` | `platform`
   - `phase`: `concept` | `ongoing-development` | `pilot-test` | `live` |
     `handover`
   - `status`: `active` | `blocked` | `paused` | `complete` | `cancelled`
   - `priority`: `high` | `medium` | `low`
3. **Ownership** - the real owner's name/email/role (add them to the
   `people` list if they're not already a user in this app) and any
   business owner name.
4. **Current next action** - whatever the vault currently says is next.
5. **Links** - repo/environment/docs URLs, if any exist (link fields
   only - no repo integration in MVP).
6. **Tech stack summary** - one line, if known.
7. **Status history** - every real, dated status update you have for
   the project (not just the latest) - `event_date`, `summary`, who wrote
   it, and optionally `completed_work` / `next_actions` / `blockers` /
   `verification_notes`. This is what establishes `data_as_of` /
   freshness (T4) once imported - the most recent `event_date` across all
   of a project's events becomes its freshness anchor.
8. **Documentation inventory** - for each artifact_type that actually
   exists for the project (`user_guide`, `admin_guide`, `developer_guide`,
   `agent_guide`, `support_runbook`, `deployment_guide`,
   `verification_matrix`, `exit_md`): its real status
   (`missing`/`draft`/`current`/`stale`/`approved`/`retired`), title, and
   source path/link if there is one. Omit artifact types that don't exist
   yet at all - T5's deterministic gap list already treats "absent" as
   `missing`.

## Why this matters beyond T6

Per `docs/MVP_TASK_PLAN.md`, these become the **AI golden set** used for
T9/T10 (structured AI summaries + rubric evaluation). Fabricated or
guessed data here would silently corrupt that evaluation later - hence
the strict, no-placeholder validation (the template ships with `"TODO"`
values that deliberately fail schema validation until replaced).

## Running it

```bash
cd backend
.venv/Scripts/python -m app.seed_import.cli --file /path/to/pilot_projects.json
```

Requires the DB migrated (`alembic upgrade head`) and the bootstrap admin
present (seeded in T2) to record as the audit actor, unless you pass
`--actor-email` for a different existing user.
