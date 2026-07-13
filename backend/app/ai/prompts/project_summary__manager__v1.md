---
prompt_id: project_summary__manager
version: 1
task_type: project_summary
audience: manager
status: draft
---

You are writing a structured status summary of an internal CWS
development project for a **manager** audience - someone tracking
portfolio progress and risk, not writing code. Use only the structured
data given below. Do not invent facts, business impact, deadlines, or
outcomes that are not present in the data.

{source_bundle}

Respond with **only** a single JSON object (no markdown fences, no
commentary before or after) matching exactly this shape:

{{
  "summary": "2-4 sentences: business-relevant current state, progress, and risk - plain language, no implementation detail.",
  "assumptions": ["any assumption you had to make because the data was incomplete - empty list if none"],
  "gaps": ["missing information, documentation gaps, or reporting gaps a manager should know about - empty list if none"],
  "recommended_next_actions": ["concrete next actions a manager could act on or escalate - empty list if none"],
  "requires_human_review": true,
  "confidence": 0.0
}}

`requires_human_review` must always be `true` - this output is a draft,
never official until a human reviews it. `confidence` is your own
estimate (0.0-1.0) of how well-grounded this summary is given the data
provided - lower it if the data is thin or the project looks stale.
