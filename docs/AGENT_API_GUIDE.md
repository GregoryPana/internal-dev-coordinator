# Agent API guide

How an AI agent (e.g. **Hermes**, the vault agent) reads project state from
the Internal Development Coordinator and writes updates back. Written to be
pasted into an agent's context or tool definition.

## Identity & auth

The agent is a provisioned service account (`ai_service_account` role) with
membership on the projects it may touch. Provision or refresh (idempotent,
re-run after new projects are created):

```bash
cd backend
python -m app.authz.provision_agent --email hermes@cws.local --name "Hermes (AI agent)"
```

Authentication (dev mode): send the account's email on every request:

```
X-User-Email: hermes@cws.local
```

Base URL: `http://localhost:8000`. Full machine-readable schema:
`GET /api/openapi.json` (no auth needed) - ideal as the agent's tool spec.

> Dev auth trusts this header, which is acceptable only on the single-user
> host. At productization the same account authenticates with a real token
> (Entra client-credentials) - the permission model below is unchanged.

## What the agent may and may not do

| Capability | Allowed? |
|---|---|
| Read projects, status events, documentation matrix, repo signals (member projects) | yes |
| Create status events (member projects) | yes |
| Update registry fields: phase, status, priority, next action, dates, percent_complete, links, flags (member projects) | yes |
| Upsert documentation-artifact rows (member projects) | yes |
| Create new projects | no (admin/developer role only) |
| Generate starter packs or AI summaries | no |
| **Review/approve/reject AI output or starter packs** | **never** - human-review gates exclude the role by design (FR-022) |
| Read/change integration settings, portfolio audit feed | no (admin/auditor) |

Every write is attributed to the agent and lands in the append-only audit
trail exactly like a human's.

## Read current state

```
GET /api/projects                             # portfolio: phase/status/priority/freshness/percent/flags
GET /api/projects/{id}                        # one project in full
GET /api/projects/{id}/status-events          # evidence timeline, newest first
GET /api/projects/{id}/documentation          # doc matrix with is_gap per artifact
GET /api/projects/{id}/repo-signals           # live/cached GitHub signals (204 = no repo, 501 = disabled)
GET /api/projects/{id}/audit-events           # who did what on this project
```

Projects are identified by `id`; `slug` is the stable natural key (e.g.
`vas-network-check`) - resolve slug→id from `GET /api/projects`.

## Write updates

**Status event** - the primary update primitive. One event per real change,
dated when it happened; this drives the freshness badge (`data_as_of` =
newest `event_date`):

```
POST /api/projects/{id}/status-events
{
  "event_date": "2026-07-14",
  "summary": "One-paragraph factual update.",
  "completed_work": "…" | null,
  "next_actions": "…" | null,
  "blockers": "…" | null,          // non-null renders as a red blocker callout
  "verification_notes": "Source: Hermes vault 'X.md', entry #N, as of YYYY-MM-DD."
}
```

**Registry fields** - PATCH with only the fields that changed:

```
PATCH /api/projects/{id}
{ "phase": "live", "status": "active", "percent_complete": 60,
  "current_next_action": "…", "expected_finish_date": "2026-07-31" }
```

Vocabulary is law - invalid values are rejected (422):
- phase: `concept | ongoing-development | pilot-test | live | handover`
- status: `active | blocked | paused | complete | cancelled`
- priority: `high | medium | low`

**Documentation artifact**:

```
PUT /api/projects/{id}/documentation/{artifact_type}
{ "title": "…", "status": "missing|draft|current|stale|approved|retired",
  "source_path": "docs/…", "owner_id": null, "last_reviewed_at": null, "notes": "…" }
```

artifact_type: `user_guide | admin_guide | developer_guide | agent_guide |
support_runbook | deployment_guide | verification_matrix | exit_md`.

## Conventions (follow these)

1. **Check before you post.** Status events have no API-level dedupe: list
   `GET /status-events` first and skip if an event with the same
   `event_date` + `summary` already exists. Never delete/edit - events are
   immutable evidence.
2. **Always cite the source** in `verification_notes`
   ("Source: <vault note>, as of <date>") so humans can trace every
   agent-written fact.
3. **Report, don't judge.** Record what the vault/register states; leave
   review decisions, approvals and quality judgments to humans.
4. **Prefer PATCH-minimal.** Send only changed fields; every PATCH is
   audited with the changed-field list.
5. **New project in the vault?** The agent cannot create it - flag it to
   Gregory; after creation, re-run the provisioning command so the agent
   gains membership.

## Errors

- `401` unknown/inactive account - provisioning missing.
- `403` not a member of that project (or a human-only action) - do not retry.
- `422` payload/vocabulary violation - fix the value, don't guess new vocab.
- `409` state-machine conflict (review flows - agent shouldn't hit these).
