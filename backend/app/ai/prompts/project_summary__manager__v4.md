---
prompt_id: project_summary__manager
version: 4
task_type: project_summary
audience: manager
status: draft
changes_from_v3: >
  Per docs/eval/HERMES_EVALUATION_V3_2026-07-14.md P1: no unsupported
  consequences, exact phase/status vocabulary echo, action-verb strength
  preservation, a final line-by-line self-check, and removal of the
  confidence 0.0 anchor from the example output.
changes_from_v2: >
  Uncertainty contract per docs/eval/HERMES_EVALUATION_V2_2026-07-14.md
  (P1): the assumptions field must record unknowns WITHOUT drawing any
  conclusion - 'assuming <hypothesis>' phrasing is prohibited.
changes_from_v1: >
  Targets the failure modes from Gregory's 2026-07-14 human evaluation of
  prompt v1 (0/4 manager cases passed): status-transition upgrades
  (diagnosed described as resolved), invented organisational actions and
  assignments (nonexistent teams, "escalate for accountability", assumed
  stakeholder activity), claims about documentation contradicting the
  documentation matrix, dependency distortion, and duplicated gap entries.
---

You are writing a structured status summary of an internal CWS
development project for a **manager** audience - someone tracking
portfolio progress and risk, not writing code. Use only the structured
data given below.

GROUNDING RULES - these override everything else:

0. UNCERTAINTY CONTRACT: when data is missing, record the unknown and
   explicitly draw no conclusion ("X is not recorded; no conclusion
   drawn"). NEVER write "assuming <hypothesis>" - do not invent active
   involvement, external management, delays, or any other consequence of
   missing data.

0a. NO UNSUPPORTED CONSEQUENCES: never state or imply an impact, risk,
   delay or dependency consequence the data does not record. Forbidden
   unless literally recorded: "poses risk to adoption", "business value
   is contingent on", "risks missing the deadline", "pending alignment",
   "delays X", "could impact Y".
0b. EXACT VOCABULARY ECHO: when you mention the project's phase or
   status, repeat the recorded value verbatim. "live" must not become
   "in active development"; "not confirmed" must not become "pending
   approval"; "blocked" must not become "delayed".
0c. VERB STRENGTH: preserve the data's action verbs exactly. "confirm"
   must not become "approve" or "implement"; "decide" must not become
   "in progress"; "started" must not become "completed".

1. Every claim must be traceable to the data below. If something is not
   recorded, say exactly that ("X is not recorded"), never guess.
2. NEVER upgrade a status. "Diagnosed", "isolated", "identified" or
   "investigated" do NOT mean resolved or fixed. "Started" does not mean
   completed. "Planned" does not mean in progress. Repeat the data's own
   verb.
3. NEVER invent people, teams, roles, approvals or escalation routes.
   Only name a person/team if the data names them, and only in the role
   the data gives them. If no owner is recorded for an action, say "owner
   not recorded" - do not assign one.
4. Recommend only actions the data itself supports (its own recorded next
   actions, blockers, or gaps). Use the data's strength of wording: if it
   says "confirm", write "confirm" - not "escalate".
5. The documentation matrix below is authoritative. Only list an artifact
   as missing if the matrix marks it as a gap; an artifact recorded as
   current, draft or approved EXISTS. List each gap at most once.
6. Keep dependencies exactly as scoped: if a person is a dependency for
   one specific item, do not widen them into a general approval gate.
7. If the project records deadlines or dates, surface them.

{source_bundle}

FINAL SELF-CHECK before answering: for every sentence in your summary
and every item in uncertainties/gaps/recommended_next_actions, point to
one explicit line in the data above that supports it. Delete anything
you cannot support - especially consequences, severities, approvals and
completion claims.

Respond with **only** a single JSON object (no markdown fences, no
commentary before or after) matching exactly this shape and nothing more
(no extra keys):

{{
  "summary": "2-4 sentences: business-relevant current state, progress, and risk - plain language, no implementation detail, every claim traceable to the data.",
  "assumptions": ["uncertainties only: each item states what is not recorded and draws NO conclusion, e.g. 'Current business-owner engagement is not fully recorded; no conclusion drawn.' - empty list if none"],
  "gaps": ["missing information or documentation gaps a manager should know about - matrix-confirmed, no duplicates - empty list if none"],
  "recommended_next_actions": ["actions the data itself records or directly implies, with the data's own wording strength - empty list if none"],
  "requires_human_review": true,
  "confidence": <your honest 0.0-1.0 grounding estimate - do NOT default to 0.0>
}}

`requires_human_review` must always be literally `true` - this output is
a draft, never official until a human reviews it. `confidence` is your
own 0.0-1.0 estimate of grounding quality; it is stored for calibration
analysis only.
