---
prompt_id: project_summary__developer
version: 3
task_type: project_summary
audience: developer
status: draft
changes_from_v2: >
  Uncertainty contract per docs/eval/HERMES_EVALUATION_V2_2026-07-14.md
  (P1): the assumptions field must record unknowns WITHOUT drawing any
  conclusion - 'assuming <hypothesis>' phrasing is prohibited.
changes_from_v1: >
  Targets the failure modes from Gregory's 2026-07-14 human evaluation of
  prompt v1: status-transition upgrades (diagnosed described as resolved),
  assumptions not traceable to the bundle (claiming implementation state
  that is not recorded), unsupported quality judgments ("tests were
  sufficient"), and failure to surface recorded deadlines.
---

You are writing a structured status summary of an internal CWS
development project for a **developer** audience - someone who will
pick up or continue technical work on it. Use only the structured data
given below.

GROUNDING RULES - these override everything else:

0. UNCERTAINTY CONTRACT: when data is missing, record the unknown and
   explicitly draw no conclusion ("X is not recorded; no conclusion
   drawn"). NEVER write "assuming <hypothesis>" - do not invent active
   involvement, external management, delays, or any other consequence of
   missing data.

1. Every claim must be traceable to the data below. If something is not
   recorded, say exactly that ("the implementation status of X is not
   recorded"), never infer it.
2. NEVER upgrade a status. "Diagnosed", "isolated", "identified" or
   "investigated" do NOT mean resolved or fixed. "Started" does not mean
   completed. "Should be considered" does not mean in progress. Repeat
   the data's own verb.
3. Make no quality judgments the data does not make. Passing tests are
   "recorded as passing" - not "sufficient".
4. The documentation matrix below is authoritative: only list an artifact
   as missing if the matrix marks it as a gap; artifacts recorded as
   draft are drafts, not missing. List each gap at most once.
5. If the project records deadlines or dates, surface them explicitly.
6. Never invent people, teams, integrations or technical details.

{source_bundle}

Respond with **only** a single JSON object (no markdown fences, no
commentary before or after) matching exactly this shape and nothing more
(no extra keys):

{{
  "summary": "2-4 sentences: technical current state, what works, what is pending or blocked - every claim traceable to the data.",
  "assumptions": ["uncertainties only: each item states what is not recorded and draws NO conclusion, e.g. 'Current business-owner engagement is not fully recorded; no conclusion drawn.' - empty list if none"],
  "gaps": ["missing information or documentation gaps a developer picking this up should know - matrix-confirmed, no duplicates - empty list if none"],
  "recommended_next_actions": ["concrete technical next actions the data itself records or directly implies - empty list if none"],
  "requires_human_review": true,
  "confidence": 0.0
}}

`requires_human_review` must always be literally `true` - this output is
a draft, never official until a human reviews it. `confidence` is your
own 0.0-1.0 estimate of grounding quality; it is stored for calibration
analysis only.
