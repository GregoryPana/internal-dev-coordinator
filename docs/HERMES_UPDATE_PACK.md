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

## Active repo tracking + in-app guided integration setup (2026-07-14, Claude Fable 5)

Gregory deferred authentication (frontend MSAL) to productization time and
said continue with other development - so this session built the approved
active-tracking + guided-setup pair from the 2026-07-14 product direction.

- **In-app integration settings** (`app/integrations`, migration
  `b7e2d81c3fa4`): admin-only Settings page + API where GitHub repo
  tracking is enabled/disabled and a PAT is stored **encrypted at rest**
  (Fernet, key = new `IDC_SECRET_KEY`, generated into Gregory's
  `backend/.env`). Credentials go in and never come back out - every
  response/audit record only says *whether* one is set
  (`credential_changed: true`, never the value). Saving a token without a
  secret key configured is refused with instructions (400), not silently
  stored weaker. In-app settings **override env vars** when a row exists;
  env remains the fallback so nothing breaks for env-configured deploys.
- **Guided setup UI** at `/settings`: states exactly what is needed
  (fine-grained PAT), the exact GitHub click-path to create it, the exact
  minimal permissions (Contents: read-only, Metadata: read-only, selected
  repos only), a paste-to-store field, a **Test connection** button
  (reports authenticated-or-not + rate-limit headroom), and status chips
  (enabled/token-stored/configured-via). This is the template for the AI
  provider card (placeholder note there for now).
- **Active repo tracking**: `repo_snapshots` table + background poller
  (asyncio loop in the FastAPI lifespan, every
  `IDC_REPO_POLL_INTERVAL_MINUTES`=30, disabled in tests). Every fetch -
  poller or profile view - persists a snapshot (success or failure);
  profile views serve a fresh cached snapshot instead of hitting GitHub
  every time. Live pass verified against the real portfolio: 7 repos
  polled, 4 ok (incl. this coordinator and the billing platform), 3
  cleanly-failed snapshots for the private repos (visible evidence of the
  missing PAT rather than silence), 10 projects without repos skipped.
- **Deliberate boundary:** snapshots do NOT touch `Project.data_as_of`.
  Whether repo activity should feed freshness changes what "data as of"
  means and stays an explicit pending decision for Gregory.
- **Test-isolation lesson hit a third time (T6, then again now):** the
  browser session committed a real `integration_settings` row and two
  tests that assumed an empty table started failing. Fixed by deleting
  rows *inside the test transaction* (rolled back afterwards). Any test
  asserting absence of rows in this shared dev DB is fragile the moment
  the feature gets real use.
- 112/112 tests; migration cycle clean; `npm run build` clean;
  Playwright-verified settings flow end to end (enable in-app -> saved ->
  profile card lit up -> snapshot persisted -> audit event recorded).

---

## PM fields, phase consolidation, edition gate, full register seed (2026-07-14, Claude Fable 5)

Direct instructions from Gregory, all landed in one session:

- **AI summary failures root-caused and fixed:** `google/gemma-4-31b-it:free`
  started returning 404 upstream (still *listed* in OpenRouter's model list,
  but dead at the completions endpoint) - that was the `provider_unavailable`
  wave; `malformed_output` was ordinary free-tier flakiness. Default model
  (code + `backend/.env`) switched to `nvidia/nemotron-nano-9b-v2:free`
  after live-probing candidates; a real VAS manager summary generated
  successfully post-fix. Lesson: a model being listed proves nothing -
  probe the completions endpoint.
- **Phase vocabulary consolidated to exactly five values** per Gregory:
  `concept`, `ongoing-development`, `pilot-test`, `live`, `handover`.
  Migration `a1c4f9d2b7e0` does the Postgres enum swap (rename old /
  create new / USING-cast / drop old - values can't be removed in place)
  and remaps existing rows: discovery→concept, build→ongoing-development,
  pilot→pilot-test, retired→handover. Downgrade is lossy by nature and
  documented as such.
- **Project-management fields on Project:** `date_commenced`,
  `expected_finish_date`, `percent_complete` (0-100, DB check constraint),
  shown as a Delivery card on the profile and a Progress column on the
  dashboard.
- **Edition gate introduced** (`IDC_EDITION=custom|product`, default
  custom, surfaced via /api/health): Gregory intends to package the app
  for others, so custom-only features are gated on this flag - never
  forked. First custom-only features: per-project `uses_process_automation`
  and `uses_ai` booleans (portfolio metrics answering "how many of our
  projects automate processes / use AI") with dashboard rollup cards.
  Product edition hides the checkboxes and the two cards.
- **Dashboard segregation:** "In delivery" (concept/ongoing-development/
  pilot-test) vs "Live & completed" (live/handover phase or complete
  status) as two separately-counted tables.
- **Full register seeded:** all 13 remaining vault register entries
  (STB OCR, ONT Device Capture, DC Onboarding, Billing Platform,
  Track B Warehouse API, Data Archiving, P&P Governance, Access
  Governance, R&D Pilots, AI-Strategy RFP, Vendor Evaluations, HR
  Application Platform, and the IDC itself) imported with real register
  data - statuses, blockers, next actions, repo/env links, and AI/
  automation flags taken from the register's own KPI classification
  (AI count: 2 = HR platform + IDC; automation count: 6). Portfolio now
  holds 17 projects; the platform now tracks itself (entry #16,
  pilot-test phase). Register→app status mapping judgment calls:
  Drafted/Idea/Planned → concept+paused (or active where work is
  demonstrably moving), Assessment/Enabling tracks typed as `prototype`
  so they only owe agent_guide/exit_md docs. The seed remains idempotent
  and gitignored.
- 105/105 tests; migration verified with a full downgrade→upgrade cycle;
  Playwright-verified at 1280/768.

---

## Post-MVP session: polish + Phase 4 + production readiness (2026-07-13, Claude Fable 5)

Gregory approved continuing past the MVP cut line on all fronts
("proceed with all the given"). Three tracks landed as three commits;
the fourth (prompt v2 iteration) stays blocked on his T10 rubric scores.

**1. Polish pass (`4aba001`)** - in-scope depth over existing records:

- Read-only audit API + UI: portfolio-wide feed at `/audit` (new authz
  gate: admin/auditor only) and per-project trail at `/projects/:id/audit`
  (anyone with project read). The audit router has GET routes only and a
  test asserts that; the append-only source-scan test was extended to
  permit an explicitly-listed read helper (`list_events`) - the write
  surface is still `record()` alone.
- FR-022 visibility gap closed: starter-pack *tailoring* AI runs were
  logged but visible nowhere. New `GET /api/projects/{id}/ai/interactions`
  (all task types) + an "AI activity log" table on the AI summary page
  showing validation/review status and token counts for every run.
- Portfolio dashboard: search/status/phase/priority/stale-only filters,
  sorting (priority / name / oldest-data-first), and the rollup cards
  (Total/Blocked/Stale) are now clickable filters.

**2. Phase 4 - GitHub READ integration (`5888404`)**:

- New `app/repo` package, deliberately mirroring the AI-provider adapter
  pattern: `IDC_GITHUB_PROVIDER=disabled` by default, 501 when disabled,
  fine-grained read-only PAT via `IDC_GITHUB_TOKEN` (optional - public
  repos work unauthenticated). A scope-guard test asserts no write verbs
  exist in the provider source, matching the scope doc's "no write
  actions to external systems."
- `GET /api/projects/{id}/repo-signals`: default branch, last push, last
  commit, open PRs, open issues (PRs subtracted from GitHub's inflated
  `open_issues_count`). 204 when the project has no parseable github.com
  URL; 502 when GitHub can't be queried. Frontend card on the project
  profile hides itself when there's nothing to say.
- **Live-verified against real repos:** `GregoryPana/b2b-cx-platform`
  and `cws-pulse-awards` are publicly visible and returned real signals
  (CWSCX's last commit = merge of PR #12, matching its status evidence);
  `health-fair-2026` and `vas-system-check` 404 unauthenticated - the
  profile shows a soft "could not reach GitHub" note for those. **A
  read-only PAT is needed to light up the two private pilots.**
- Test-isolation lesson re-applied preemptively: conftest's autouse
  fixture now forces `github_provider=disabled` too, so a future token in
  `.env` can never make the suite hit live GitHub.

**3. Production readiness (`ef5a469`)**:

- Entra token validation is real now: `app/authz/entra.py` validates
  Bearer JWTs against the tenant JWKS (RS256/issuer/audience/expiry via
  PyJWT); the email claim must still match an active Person row, so
  Entra provisioning alone grants nothing. In entra mode the dev
  X-User-Email header is ignored (tested with locally-signed tokens).
- Docker packaging: backend image runs `alembic upgrade head` before
  serving; frontend image is a Vite build served by nginx that proxies
  `/api` same-origin to the backend; `docker-compose.prod.yml` keeps the
  DB off the host network and refuses to start without IDC_DB_PASSWORD.
  Full stack smoke-tested on a fresh volume through nginx.
- `docs/DEPLOYMENT.md` runbook: config rules, Entra app-registration
  steps, backup/restore/upgrade/rollback, and known limits.
- Gotcha worth remembering: **docker compose silently reads `./.env`
  (the dev file) for interpolation when `--env-file` is omitted** - the
  smoke test surfaced dev values leaking into the "prod" stack that way.
  Runbook now says always pass `--env-file .env.prod`; `.gitignore` now
  covers `.env.*` so `.env.prod` can never be committed.

**Open items from this session (for the vault):**

- **Frontend Entra sign-in (MSAL) is not wired.** The backend fully
  validates tokens, but the React app still sends the dev header. This is
  the single biggest gap between "packaged" and "multi-user production",
  and it needs the Entra app registration to exist first (Gregory:
  DEPLOYMENT.md section 3).
- **Read-only GitHub PAT** wanted so repo signals work for the two
  private pilot repos.
- T10 rubric scoring still pending (see T10 entry below) - prompt v2
  iteration waits on it.

**Product direction from Gregory (2026-07-14) - for the full platform:**

- **Active tracking of all working platforms/repos**, not just
  read-on-page-view: the current repo-signals integration fetches live
  when a profile is opened and stores nothing. Full platform should
  actively track every connected project (scheduled polling or webhooks),
  persist activity, and feed it into portfolio-level visibility - which
  also reopens the deferred question of whether repo activity should
  influence freshness/`data_as_of` semantics.
- **Built-in guided setup/connection assistance** for both new projects
  and existing ones: the app itself should walk a user through connecting
  everything - state exactly what is needed (e.g. a fine-grained
  read-only GitHub PAT with metadata/contents scope), show how to fetch
  it (where in GitHub/Entra to click), and accept it in-app. Integration
  configuration (repo connection, tokens, provider settings) must be
  editable/addable/removable inside the application, not env-file-only
  as today. Implies: per-project (or org-level) integration settings UI,
  secure server-side credential storage (encrypted at rest, never exposed
  back to the client), connection-test feedback, and setup-status
  indicators ("repo connected / token missing / token expired").

---

## T10 - Golden set + rubric evaluation (2026-07-13, Claude Sonnet 5)

- **Action needed from Gregory:** `docs/eval/golden_set_report_v1_2026-07-13.md`
  has 7 real, grounded, audience-differentiated AI summaries (one failed
  cleanly on a model hiccup) with blank rubric-scoring tables per
  `docs/eval/RUBRIC.md`'s 5 dimensions. This is the one part of T10 an
  agent shouldn't do - the vault plan says explicitly "Gregory scores on
  every prompt version change." Please fill in the scores; the Phase 3
  gate's "rubric pass" criterion depends on it.
- **Scope boundary respected:** the architecture spec's Deferred section
  explicitly excludes a standalone "evaluation service" from MVP scope.
  So T10 is CLI tooling only (`python -m app.ai.eval.run_golden_set`,
  same shape as T6's seed-import CLI) - no new API endpoints, no new DB
  tables, no persisted "GoldenSet"/"RubricScore" entities. The report is
  a markdown file in `docs/eval/`, not a product feature.
- **8 bundles, not "~10" - flagged, not silently padded.** The vault plan
  says "~10 golden bundles"; there are only 4 real pilot projects from
  T6, so 4 x 2 audiences = 8. Getting to 10 would mean either importing a
  5th pilot (out of scope - seed import is one-shot, not something to
  re-run to pad a number) or inventing meaningless duplicate bundles
  against the same 4 projects, which would violate the "never fabricate"
  principle just as much as inventing pilot data would have in T6. 8 real
  bundles beats 10 with 2 fake ones.
- **Free-tier volatility made 3 real runs necessary to get good coverage,
  and that itself is useful evidence:** first attempt (default model
  `google/gemma-4-31b-it:free`) got 4/8; a same-day retry got only 2/8 -
  congestion on that specific model had clearly gotten worse since T8/T9
  testing, confirming this really is a moving target, not a one-time
  fluke. Checked OpenRouter's live model list, found
  `nvidia/nemotron-nano-9b-v2:free` responding reliably, and reran with
  `IDC_AI_MODEL` overridden just for that invocation (not changing the
  shipped default, which stays `google/gemma-4-31b-it:free` for now) -
  got 7/8. **Practical takeaway for anyone re-running the golden set
  later:** if the default model is having a bad day, check
  `GET https://openrouter.ai/api/v1/models` (no auth needed) for a
  currently-healthy free model and pass `IDC_AI_MODEL=<model> python -m
  app.ai.eval.run_golden_set` rather than waiting it out or concluding
  the harness is broken.
- **The one real failure in the final report (`health-fair-2026` /
  manager, `malformed_output`) was left in the report rather than
  silently re-run until clean.** An evaluation report that only shows
  successes would misrepresent how the pipeline behaves in practice -
  the failure-handling path itself is part of what's being evaluated.

## T9 - Source-bundle builder + AI project-summary task (2026-07-13, Claude Sonnet 5)

- **"Never see what the user can't" is enforced structurally, not by
  convention.** `app.ai.source_bundle.build()` takes an already-fetched
  `Project` and does no permission checking of its own - the router calls
  `authz.require_read()` before the bundle builder is ever invoked, so
  there is no code path where the AI summary task can see a project the
  requesting user's role wouldn't already let them view directly. Worth
  keeping this shape (authz first, bundle builder trusts its input)
  rather than duplicating permission logic inside the AI layer.
- **Stale caveats (FR-023) are enforced deterministically, not left to
  prompt compliance.** The prompt asks the model to flag staleness, but
  `_enforce_stale_caveat()` in `summary_service.py` checks
  `Project.is_stale` itself and appends a caveat to `gaps` if the model's
  own output doesn't already mention it. Same design philosophy as T8's
  forbidden-data scanning: don't trust the model to reliably do the
  safety-critical thing, verify and correct in code.
- **`AIInteraction.source_ids_json` is my code's record of what was
  actually included in the bundle, not the model's self-reported
  `source_ids`.** The structured output schema still asks the model for
  its own view (per architecture spec 11.4's suggested field list), but
  that's stored in `output_json`, not treated as the audit-grade source
  citation - models can misremember or invent IDs, deterministic bundle
  construction can't.
- **No deterministic fallback exists for this task, unlike T8's starter
  packs.** A project summary is inherently AI-generated; if the provider
  fails or output is malformed, there's nothing sensible to fall back to
  - the correct behavior is a cleanly recorded failed `AIInteraction`
  (`validation_status`/`error_category` set, `output_json=null`) that the
  UI shows as "this attempt failed, try again," not a crash and not a
  fabricated summary.
- **Real free-tier volatility observed again, and handled correctly
  under real conditions, not just mocked:** during live browser testing
  against the real VAS Network Check pilot, 3 of 4 generation attempts
  succeeded with genuinely useful, varied, grounded summaries (correctly
  citing VAS's real missing docs), and 1 hit the same OpenRouter 429-
  after-retries congestion documented in the T8 addendum - it rendered as
  a clean "Rejected / Failed" card in the same list, no crash, no console
  error. This is the intended behavior, not a bug: free-tier AI output
  should degrade to a visible, retryable failure, never a silent one.

## T8 addendum - real OpenRouter provider wired and verified live (2026-07-13, Claude Sonnet 5)

- **Provider approved by Gregory**: OpenRouter, specifically because it
  fronts free-tier models and doesn't force a budget/vendor decision
  before T10's golden-set evaluation exists. Resolves the open item from
  the T8 entry below.
- **Security incident, caught before it reached git history:** Gregory
  pasted the real API key into `.env.example` (a tracked file) instead
  of `.env` (gitignored). It was never committed - caught via `git
  status`/`git diff` before any commit happened - but I moved the real
  key to `backend/.env` (the file `app/config.py` actually reads,
  relative to the backend/ working directory) and restored
  `.env.example` to a placeholder immediately. No rotation needed since
  it never entered version control, but worth remembering: **always
  verify a secret landed in a gitignored file, not just "a .env-looking
  file," before treating it as safe** - the filename similarity
  (`.env` vs `.env.example`) is an easy mistake to make under time
  pressure, for a human or an agent.
- **Finding: OpenRouter free-tier models 429 unpredictably even for a
  brand-new, zero-usage key.** Confirmed via OpenRouter's own `/api/v1/key`
  endpoint that the key had `usage: 0` and no account-level restriction -
  the 429s are shared upstream congestion on popular free models, not a
  configuration problem. Model choice matters in practice: the initial
  pick (`openai/gpt-oss-120b:free`) failed repeatedly; `google/gemma-4-31b-it
  :free` responded reliably (3/3 in a row) and became the default. Added
  bounded retry/backoff (3 retries, honors `Retry-After`) to
  `OpenRouterProvider` regardless, since this is evidently normal
  operating behavior for the free tier, not a rare edge case - a
  starter-pack generation should not fail just because a free model
  hiccuped once.
- **Test-isolation bug found the same day it could have gone unnoticed
  for a while:** once `backend/.env` had real OpenRouter config, the
  full test suite silently started making live network calls in
  whichever test relied on the *implicit* default of
  `IDC_AI_PROVIDER=disabled` - one test's runtime jumped from ~3s total
  suite time to 60+ seconds for that single test, which is how it was
  caught. Fixed with an autouse `conftest.py` fixture that forces
  `ai_provider="disabled"`/`ai_api_key=""` for every test unless a test
  explicitly overrides it. **General lesson for this repo: never assume
  a Settings default holds during tests once a developer's local `.env`
  can override it - force the value explicitly in test setup.**
- **Verified live, not just against mocks:** a direct `get_provider().
  complete(...)` call, then a full real `generate → review → export`
  cycle against the actual CWS Pulse Awards pilot project, produced a
  genuinely AI-written, grounded README paragraph (distinct from the
  deterministic fallback text) with a real `AIInteraction` row
  (`passed`/`generated`, real token counts and latency). Test rows
  cleaned up afterward.

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

- **Score the T10 golden set.** `docs/eval/golden_set_report_v1_2026-07-13.md`
  is ready for Gregory's rubric scores (see the T10 entry above and
  `docs/eval/RUBRIC.md`). This is the last open item before the Phase 3
  gate can be marked fully met.
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
- ~~Production AI provider route approval outstanding~~ - **resolved
  2026-07-13**: Gregory approved OpenRouter (free-tier model, currently
  `google/gemma-4-31b-it:free`), a real key is in `backend/.env`
  (gitignored), and a live generate→review→export cycle has produced
  real AI-tailored output. See the T8 addendum entry above. This also
  unblocks T9 (Phase 3 AI summary task) for real-provider testing, though
  free-tier 429 volatility means T9's tests should follow T8's pattern of
  testing against a fake/mocked provider, reserving live calls for manual
  smoke checks.
- **Free-tier model reliability is a live, moving target.** OpenRouter's
  free models 429 unpredictably and which model is "currently reliable"
  can change hour to hour (see the T8 addendum). If `google/gemma-4-31b-it
  :free` starts failing consistently, re-check OpenRouter's live model
  list (`GET https://openrouter.ai/api/v1/models`, no auth needed) and
  swap `IDC_AI_MODEL` - the retry/backoff in `OpenRouterProvider` handles
  transient failures, but a fully saturated model needs a different pick.
