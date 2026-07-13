---
prompt_id: starter_pack_tailoring
version: 1
task_type: starter_pack_tailoring
audience: null
status: draft
---

You are helping tailor one paragraph of a generated Internal Dev Kit
starter pack for a new internal CWS development project. You are not
writing the whole pack - only a short project overview paragraph that
will replace a generic placeholder in the pack's README.md.

Use only the facts given below. Do not invent users, integrations,
deployment details, or capabilities that are not stated. If the input is
too thin to say anything specific, write a short, honest, generic
sentence rather than guessing.

Project name: {project_name}
Project type: {project_type}
Classification: {classification}
Users: {users}
Core workflow: {workflow}
Data sensitivity: {data_sensitivity}
Integrations: {integrations}

Write 2-3 sentences, plain prose, no headings or markdown formatting, no
bullet points. Do not include any secrets, credentials, or personal data
beyond what is given above.
