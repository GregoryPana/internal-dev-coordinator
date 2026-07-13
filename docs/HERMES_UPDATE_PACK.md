# Hermes update pack - running dev log

Purpose: this repo's Hermes vault (`04 - Projects/CWS DTO/` on the vault
host) is not reachable from every agent environment that works on this
codebase - notably, a Windows-hosted Claude Code session has no filesystem
access to `/home/gpanagary/.hermes/`. This file is the bridge: a running,
in-repo log of decisions, findings and notable deviations from each work
session, written so Gregory (or Hermes) can fold it into the vault without
re-deriving context from diffs.

Complements, not duplicates:
- `docs/VERIFICATION_MATRIX.md` — what was verified, how (evidence log).
- `EXIT.md` — current handover state (point-in-time snapshot).
- This file — narrative: what was decided, what was found, why, and any
  open questions worth vault-side follow-up.

Newest entries first. Each entry: task, date, agent, then notes.

---

## T8 - AI tailoring + review workflow + zip export (2026-07-13, Claude Sonnet 5)

- **Open item resolved by design, not by picking a provider:** the MVP
  Implementation Plan's open items list "Production AI provider route
  approval" as still pending, and no provider/key/budget has been
  approved. Rather than block T8 on that decision or silently pick a
  provider, the adapter is built so `IDC_AI_PROVIDER=disabled` (the
  existing default) is a fully first-class path: starter-pack
  generate/review/export works completely today, with no AI, and no
  `AIInteraction` row is fabricated for a run that never happened
  (`app.ai.provider.get_provider()` raises `NotImplementedError` for any
  other provider name, which the router turns into a clean 501 rather
  than a crash). Wiring a real provider later is adding one file
  (`app/ai/provider.py`'s `get_provider()`), not a redesign - the whole
  generate→tailor→persist→review→export pipeline is provider-agnostic
  and already tested against a fake provider.
- **Scope decision on what "AI tailoring" means for T8:** rather than
  have a model rewrite all 11 generated files (a much bigger, harder-to-
  validate undertaking), tailoring is scoped to one grounded paragraph -
  the README's project overview - built from a prompt that explicitly
  forbids inventing users/integrations/capabilities not already in the
  structured intake. Keeps the blast radius of a bad/hallucinated
  response to one paragraph, and keeps output validation simple (non-
  empty, forbidden-data-clean) instead of needing a multi-file parsing/
  schema-validation layer for MVP.
- **Forbidden-data scanning runs before the provider is ever called**,
  not just on the response - `app.ai.forbidden_data.scan_many()` checks
  the intake text first; if it finds something secret-shaped, the AI
  call is skipped entirely (verified in `test_ai_tailoring_forbidden_data
  _in_intake_skips_call`, which asserts the fake provider's call count
  is exactly 0) and an `AIInteraction` row records the refusal
  (`failed_forbidden_data` / `rejected`) so there's a durable audit trail
  of the safety control actually firing, not just silence.
- **Same enum-type-reuse migration bug as T5, same fix:** `starter_packs.
  status` and `ai_interactions.human_review_status` share one Postgres
  enum type created fresh in this migration; the second reference needed
  `create_type=False` and the `downgrade()` needed to explicitly drop
  all 5 new enum types. This is now the third time this exact class of
  bug has been hit and fixed - worth turning into a standing pre-flight
  check ("does this migration create 2+ columns referencing the same new
  or existing Postgres enum type?") before running a fresh migration on
  future enum-touching tasks (T9's `AIInteraction` reuse of these same
  types didn't hit it again, since T8 already created them).
- **e2e was run against a real pilot project** (CWSCX Platform, imported
  in T6) end to end through the actual browser download API, not a
  mocked fetch - the exported zip was opened afterward and its 11
  filenames checked directly.

## T7 - Deterministic starter-pack templates + intake form (2026-07-13, Claude Sonnet 5)

- **Scope discipline decision:** T7 does not create a `StarterPack` DB row
  or touch persistence at all - the vault plan explicitly assigns
  "StarterPack + AIInteraction + audit records" to T8, and the risks list
  names "scope regrowth through starter-pack templates" as something to
  watch. So `POST /api/projects/{id}/starter-pack/preview` is fully
  stateless: it returns the 11 generated files in the response and
  records only an audit event (`starter_pack_generated`, `object_id`
  null since there's no `StarterPack` row yet). No migration in this
  task at all.
- **FR-016 file list is frozen and tested as a set-equality check** (`tests/
  test_starterpack.py::test_preview_generates_exactly_the_fr016_file_list`)
  - exactly `README.md`, `EXIT.md`, `OPENCODE.md`, `CLAUDE.md`,
  `AGENTS.md`, `docs/PROJECT_SCOPE.md`, `docs/ARCHITECTURE.md`,
  `docs/DATA_MODEL.md`, `docs/DEPLOYMENT.md`, `docs/OPERATIONS.md`,
  `docs/VERIFICATION_MATRIX.md`. Adding a 12th file later should fail this
  test until it's a deliberate, reviewed change to FR-016 itself.
  `project_type`/`classification` already live on `Project` and drive
  template selection directly - the intake form only captures what
  `Project` doesn't (users, workflow, data sensitivity, integrations,
  deployment target), matching FR-014.
- **Template content is modeled on this repo's own real files**, since
  the vault's MVP Implementation Plan explicitly calls this repo's own
  bootstrapping "the first starter-pack validation" - e.g. the generated
  `EXIT.md` mirrors the real structure found in the Health Fair pilot's
  own `EXIT.md` (System owner / Business owner / Technical owner /
  Runtime / Environment variables / Deployment / Backup and retention /
  Known risks), and `AGENTS.md` mirrors this repo's own read-first/hard-
  rules/verification-before-done structure.
- **Template selection by project_type is real, not cosmetic:** verified
  in both a unit test and a live browser run against the real VAS
  Network Check project (`operational-tool`) that `docs/DEPLOYMENT.md`
  gets the systemd-only pattern (no NGINX) and `AGENTS.md`/
  `docs/DATA_MODEL.md` list only the artifact types VAS's project_type
  actually requires (`developer_guide, agent_guide, support_runbook,
  deployment_guide, verification_matrix, exit_md` - no `user_guide` or
  `admin_guide`), pulled live from `vocab.REQUIRED_DOC_PROFILES` rather
  than hard-coded per file.

## T6 - Vault seed import: real pilot data imported, Phase 1 gate met (2026-07-13, Claude Sonnet 5)

- **Resolved:** Gregory supplied the vault path
  (`C:\Users\gpanagary\Hermes Knowledge Vault`), which resolved the T3-T5
  blocker below - it's a normal Windows path, just not one this session
  had been told about yet (not the `/home/gpanagary/.hermes/` path
  referenced in the docs, which still doesn't exist here; that reference
  may be stale or specific to a different, non-Windows agent environment -
  worth Gregory confirming which is authoritative).
- **Source used:** `04 - Projects\CWS DTO\Internal Development Project
  Register.md`, entries #3 (CWSCX), #4 (Pulse Awards), #5 (VAS), #15
  (Health Fair), all reflecting state as of 2026-07-13. Cross-checked
  documentation-artifact inventory against each project's actual repo on
  this machine (`scratch/cx-b2b-platform`, `scratch/pulse-awards`,
  `scratch/VAS_Network_Check`, `scratch/health-fair-26`) rather than
  guessing from the register's narrative alone - e.g. confirmed Health
  Fair's `EXIT.md` is genuinely a draft (it says so itself: "must be
  completed", `TBD` owner) rather than assuming status from the register
  text.
- **Scope deviation, flagged not silently decided:** imported **both**
  CWSCX and Pulse Awards, even though `docs/PROJECT_SCOPE.md` says "Pulse
  Awards or CWSCX" (pick one). Both had equally good real source data and
  no reason favored dropping either - low-risk, easily reversed (delete
  the row) if Gregory wants exactly 3.
- **Real data landed:** CWSCX Platform (live/platform/high, active),
  CWS Pulse Awards (build/reusable/medium, active), VAS Network Check
  (live/operational-tool/medium, active), Health Fair 2026
  (build/one-off/high, **blocked** - matches the register's explicit
  "final content/auth/deployment blocked"). One real, dated status event
  per project; 13 real documentation-artifact rows (agent_guide/exit_md/
  deployment_guide/support_runbook, only where a matching file actually
  exists in the repo - the other 4 artifact types are genuinely absent
  and correctly show as gaps, not guessed at).
- **`docs/MVP_TASK_PLAN.md` T6 now checked; Phase 1 gate marked met**
  (4 pilots exceeds the 3-project minimum; gap lists verified against
  real on-disk doc state; audit trail populated; zero AI).
- **Real import data location:** `backend/seed_data/pilot_projects.json`,
  gitignored (`backend/seed_data/` added to `.gitignore`) since it
  contains real internal project details - it will not appear in the git
  history.
- **Test-isolation bug found and fixed by the real data itself:**
  `tests/test_registry.py::test_manager_sees_all_projects_developer_sees_only_membership`
  asserted the portfolio-wide manager view returned exactly 2 projects,
  silently assuming an empty `projects` table. The real seed data broke
  that assumption (correctly - the assumption was never actually safe).
  Fixed to assert the two test-created project IDs are a subset of the
  manager's visible set instead of asserting an exact count. Worth
  remembering: any future test asserting an exact global count against
  this shared dev DB is fragile the moment real data exists in it.
- **Next step:** none for T6 itself - this task is done. T7 (deterministic
  starter-pack templates + intake form) is next per `docs/MVP_TASK_PLAN.md`.

## T5 - Documentation matrix + RequiredDocProfile + deterministic gap list (2026-07-13, Claude Sonnet 5)

- **Design decision:** `RequiredDocProfile` is a real, queryable table (not
  just read from `vocab.REQUIRED_DOC_PROFILES` at request time), seeded
  from that constant via the migration - one row per every
  (project_type, artifact_type) pair, `required` true/false. This matches
  `docs/MVP_TASK_PLAN.md`'s explicit listing of it as its own entity (it
  also carries a `notes` field the vocab constant doesn't have) while still
  treating `vocab.py` as the source of truth for the initial seed values.
- **Design decision:** "gap" is deliberately narrow and deterministic -
  `required AND (no artifact row OR status == missing)`. A registered
  `draft` or `stale` artifact is *not* a gap (it exists, just not in great
  shape); this keeps T5 to "does required documentation exist at all",
  leaving quality/staleness judgment to a human, not the gap list. No AI
  involved anywhere in this task, per the AI boundary in `AGENTS.md`.
- **Finding (real bug, caught by a full downgrade→upgrade cycle test, not
  by the normal single-direction `alembic upgrade head` check):** the
  autogenerated migration created two new Postgres enum types
  (`artifact_type`, `artifact_status`) via `create_table`, but the
  autogenerated `downgrade()` only dropped the tables, not the enum types.
  A downgrade followed by a re-upgrade hit `type "artifact_type" already
  exists`. Also hit a related but distinct error first: reusing the
  *existing* `project_type` enum in this new migration's `create_table`
  needed `postgresql.ENUM(..., create_type=False)` (plain
  `sa.Enum(...)` tried to `CREATE TYPE project_type` again and collided
  with the one T2 already created), and the seed `op.bulk_insert` needed
  its `sa.table()` columns declared with the same `postgresql.ENUM(...,
  create_type=False)` type (not `sa.String`) or Postgres rejected the
  insert with a `DatatypeMismatch` (varchar vs. enum). All three fixed in
  `alembic/versions/4ab1e74e4ec3_documentation_matrix_tables.py`; the
  downgrade now explicitly drops both new enum types. **Worth remembering
  for any future migration that reuses an existing Postgres enum column
  type or introduces a new one**, since Alembic's autogenerate does not
  get any of this right by default.

## T4 - StatusEvent create/list + freshness computation (2026-07-13, Claude Sonnet 5)

- **Design decision:** `Project.data_as_of` is fully derived, never
  user-editable. On every `StatusEvent` create it is recomputed as
  `MAX(event_date)` across *all* the project's status events (not just
  compared against the incoming event) - this makes freshness correct even
  if someone backfills an older-dated event after a more recent one already
  exists. `ProjectUpdate` schema deliberately has no `data_as_of` field to
  enforce this.
- **Finding (frontend, caught by browser verification, not by build/tests):**
  the portfolio table used default (auto) table layout, so Tailwind's
  `truncate` class had no width to truncate against - the "next action"
  column overflowed past the card edge at 768px instead of ellipsizing.
  Fixed with `table-fixed` + explicit `<colgroup>` widths. Repeated
  build+typecheck alone would never have caught this; only the Playwright
  screenshot pass did. Worth remembering for any future table work in this
  app.
- **Tooling note:** no browser-automation tool was preloaded in this
  Windows Claude Code session. Used `npx playwright install chromium` +
  a scratch Node driver script (following the repo's `/run` skill
  `playwright.md` pattern) to get real browser + console-error evidence.
  Playwright was installed to the session scratchpad, not the frontend
  `package.json` — it is not a project dependency.

## T3 - Project CRUD + portfolio dashboard + project profile (2026-07-13, Claude Sonnet 5)

- **Design decision:** slug is server-generated from `name` (or an
  explicit `slug` on create) and is immutable after creation - `PATCH`
  never touches it, even if `name` changes. Duplicate slugs get a numeric
  suffix (`-2`, `-3`, ...) rather than rejecting the create.
- **Design decision:** portfolio-wide read (`admin`, `manager`, `auditor`)
  vs. membership-scoped read (`developer_project_owner`, `trainee`,
  `ai_service_account`) is enforced at the list-query level in
  `app.registry.service.list_projects_for_user`, not by filtering a
  full list in Python - keeps it correct as the registry grows.
- **Test infra note:** there was no DB test fixture yet. Added
  `backend/tests/conftest.py` using the standard SQLAlchemy
  SAVEPOINT-per-test recipe against the real dev Postgres (not a
  mocked/sqlite DB) - endpoints call `session.commit()`, so a plain outer
  transaction would end on the first commit; the fixture restarts a
  nested transaction after every commit via the `after_transaction_end`
  event. This is now the pattern for all future integration tests in this
  repo (used again in T4's `test_status.py` unchanged).
- **Frontend scope decision:** introduced Tailwind now (was a bare Vite/
  React scaffold before T3) per `DESIGN.md`'s explicit instruction to add
  it "as a deliberate design-system implementation step." Semantic tokens
  (`background`, `surface`, `primary`, `danger`, etc.) defined once in
  `tailwind.config.js`, matching `DESIGN.md` section 5 exactly.
- **Known environment quirk:** `npm install` on this Windows box can hit
  the documented `@rollup/rollup-win32-x64-msvc` optional-dependency bug
  (npm/cli#4828) after a partial install. Fix is a clean
  `rm -rf node_modules package-lock.json && npm install` - not a code
  issue, just an npm/Windows interaction worth knowing before assuming a
  build failure is real.

---

## Open items for vault follow-up

- **Confirm the correct Hermes vault path.** `docs/PROJECT_SCOPE.md` /
  `docs/AGENT_DESIGN_SKILLS.md` reference `/home/gpanagary/.hermes/...`
  (a path this Windows session cannot see), but the actual vault turned
  out to be `C:\Users\gpanagary\Hermes Knowledge Vault`. Worth Gregory
  confirming whether the `.hermes` path is a different (e.g. WSL/Linux)
  environment's mirror of the same vault, or a stale reference that
  should be corrected in those docs.
- **Decide whether to keep both CWSCX and Pulse Awards** as golden-set
  pilots (T6 imported both instead of picking one per
  `docs/PROJECT_SCOPE.md`'s "Pulse Awards or CWSCX" wording) - no action
  needed if four pilots is fine, otherwise delete one project row.
- **Production AI provider route approval still outstanding.** T8 built
  the full generate/review/export pipeline and the provider adapter, but
  `IDC_AI_PROVIDER=disabled` is the only implemented path - no real model
  has ever produced output for this app. Once Gregory approves a
  provider (Anthropic/OpenAI/Azure OpenAI per the architecture spec's
  recommended route), that's a small, contained addition
  (`app/ai/provider.py`), not a redesign - but it does need the SDK added
  as a dependency and a key/budget decision, which is explicitly outside
  what an agent should decide unilaterally. This also blocks T9 (the
  Phase 3 AI summary task) from producing real output, though T9's
  source-bundle builder and validation logic can still be built and
  tested against a fake provider the same way T8 was.
