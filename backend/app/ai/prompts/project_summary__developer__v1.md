---
prompt_id: project_summary__developer
version: 1
task_type: project_summary
audience: developer
status: draft
---

You are writing a structured status summary of an internal CWS
development project for a **developer** audience - someone who will
pick up or continue technical work on it. Use only the structured data
given below. Do not invent facts, integrations, deadlines, or technical
details that are not present in the data.

{source_bundle}

Respond with **only** a single JSON object (no markdown fences, no
commentary before or after) matching exactly this shape:

{{
  "summary": "2-4 sentences: current technical state, what's been done, what's blocking or next, written for someone who will write code on this project.",
  "assumptions": ["any assumption you had to make because the data was incomplete - empty list if none"],
  "gaps": ["missing information or documentation gaps a developer should know about - empty list if none"],
  "recommended_next_actions": ["concrete next technical steps, grounded in current_next_action/status events - empty list if none"],
  "requires_human_review": true,
  "confidence": 0.0
}}

`requires_human_review` must always be `true` - this output is a draft,
never official until a human reviews it. `confidence` is your own
estimate (0.0-1.0) of how well-grounded this summary is given the data
provided - lower it if the data is thin or the project looks stale.
