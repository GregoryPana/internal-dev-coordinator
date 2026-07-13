# Architecture

## Shape

**Modular monolith.** One FastAPI application, one PostgreSQL database, one React/TypeScript frontend. No separate services, brokers, or extra datastores.

```text
React UI (frontend/)
  -> FastAPI API (backend/app, one application)
      -> app.authz          single authorization choke point
      -> app.registry       projects, phase/status, ownership, portfolio/profile
      -> app.status         status events, current next action, blocker state, freshness
      -> app.docs_matrix    documentation artifacts, required-doc profiles, deterministic gaps
      -> app.starterpack    intake, templates, generation, review, zip export
      -> app.ai             source-bundle builder, prompt files, provider adapter,
                            output validator, AIInteraction log
      -> app.audit          append-only events, evidence references
      -> app.seed_import    one-shot CSV/JSON import of pilot projects
      -> PostgreSQL (one database, Alembic migrations)
```

## Key decisions

| Decision | Choice |
|---|---|
| Auth | Real role/permission model from day one; dev-auth login stub for local MVP; Entra/OIDC production target. Second user => Entra mandatory. |
| Async work | Postgres-backed `jobs` table + simple worker loop. No Celery/Redis. |
| AI provider | Adapter abstraction (`app/ai/provider.py`); model/provider swappable; approved cloud API model for MVP, metadata-only inputs. |
| Prompts | Versioned markdown files in `backend/app/ai/prompts/`; version recorded on every run. |
| AI access control | Source-bundle builder enforces the requesting user's permissions — AI can never see what the user cannot. |
| Forbidden data | Secret-like scans on user free text, AI input bundles and AI outputs. No secrets/.env/PII to AI. |
| Audit | Append-only table; no update/delete paths in the app layer. |
| Freshness | `data_as_of` computed from latest status event; stale > 14 days; caveats required in AI output. |
| Retrieval | Structured DB fields only for MVP. No RAG over document content, no embeddings, no full-text engine. |
| Frontend | Vite + React + TS, plain fetch, no state library until needed. |
| Deployment target | Internal Dev Kit pattern: NGINX reverse proxy, systemd backend service, Docker Compose Postgres. Not set up until pilot needs it. |

## Deferred (do not scaffold)

Reporting module, integration module, evaluation service, notification service, Repository/RepoSnapshot/Environment entities, vector search, prompt DB tables.
