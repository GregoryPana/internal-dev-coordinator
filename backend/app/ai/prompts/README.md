# Prompt files

Versioned prompt assets for the AI tasks. One file per task/audience combination, named `<task_type>__<audience>__v<N>.md`, each starting with a version header:

```markdown
---
prompt_id: project_summary__manager
version: 1
task_type: project_summary
audience: manager
status: draft
---
```

Rules (see AGENTS.md and the CWS AI Implementation Best Practices framework):

- Every AI run records the prompt_id and version in its `AIInteraction` row.
- Major changes bump the version and require golden-set rubric rerun; keep the previous version file for rollback.
- MVP task types: `project_summary` (T9), `starter_pack_tailoring` (T8). No other prompts in MVP.
