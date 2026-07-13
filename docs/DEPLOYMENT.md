# Deployment runbook

Production-shaped deployment of the Internal Development Coordinator:
three containers (Postgres, FastAPI backend, nginx frontend) via
`docker-compose.prod.yml`. Local development keeps using
`docker-compose.yml` (db only) + `uvicorn` + `vite` and is unaffected.

## 1. Prerequisites

- Docker Engine + Compose v2 on the target host (internal VM / DMZ per CWS
  hosting decision).
- An Entra app registration (section 3) unless running a single-user pilot
  with `IDC_AUTH_MODE=dev`.

## 2. Configure

Create `.env.prod` next to `docker-compose.prod.yml` (never commit it):

```env
IDC_DB_PASSWORD=<strong random password>       # required
IDC_HTTP_PORT=8080                             # host port for the UI
IDC_AUTH_MODE=entra                            # dev only for a single-user pilot
IDC_ENTRA_TENANT_ID=<tenant guid>
IDC_ENTRA_CLIENT_ID=<app registration client id>
IDC_AI_PROVIDER=disabled                       # or openrouter + model + key
IDC_GITHUB_PROVIDER=disabled                   # or github + read-only PAT
# IDC_GITHUB_TOKEN=github_pat_...              # fine-grained, read-only
```

Rules that must hold:

- Secrets (`IDC_DB_PASSWORD`, `IDC_AI_API_KEY`, `IDC_GITHUB_TOKEN`) live only
  in `.env.prod` on the host. Verify with `git check-ignore .env.prod` before
  the first `up`.
- `IDC_AUTH_MODE=dev` in production is only acceptable while Gregory is the
  sole user (the X-User-Email header is trusted in dev mode). The moment a
  second person gets access, switch to `entra`.
- **Always pass `--env-file .env.prod`.** Docker Compose silently falls back
  to reading `./.env` (the local dev file) for variable interpolation when no
  `--env-file` is given, so dev values would leak into the prod stack.

## 3. Entra app registration (one-time)

1. Entra admin center → App registrations → New: "CWS Internal Dev
   Coordinator", single-tenant.
2. Expose an API → add scope `access_as_user` (or use the default
   `api://<client-id>` audience).
3. Copy the Directory (tenant) ID → `IDC_ENTRA_TENANT_ID`, Application
   (client) ID → `IDC_ENTRA_CLIENT_ID`.
4. The backend validates: RS256 signature against the tenant JWKS, issuer
   `https://login.microsoftonline.com/<tenant>/v2.0`, audience = client ID,
   expiry. Identity = `preferred_username`/`email` claim, which must match an
   **active Person row** - provisioning a user in Entra does not grant access
   until they exist in `people` with a role.
5. Frontend sign-in (MSAL acquiring tokens and sending
   `Authorization: Bearer`) is not built yet - see "Known limits" below.

## 4. Start

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

The backend container runs `alembic upgrade head` before serving, so the
schema is always current. Verify:

```bash
curl -s http://localhost:8080/api/health   # {"status":"ok",...}
```

First-time setup: the bootstrap admin seed (Gregory) is created by the
migrations. Import pilot data if starting from an empty DB:

```bash
docker compose -f docker-compose.prod.yml exec backend \
  python -m app.seed_import.cli seed_data/pilot_projects.json
```

(requires copying the real `seed_data/pilot_projects.json` into the
container or bind-mounting it - it is gitignored and not baked into images).

## 5. Operate

- **Logs**: `docker compose -f docker-compose.prod.yml logs -f backend`
- **Backup**: `docker compose -f docker-compose.prod.yml exec db pg_dump -U idc idc > idc_$(date +%F).sql`
- **Restore**: `docker compose -f docker-compose.prod.yml exec -T db psql -U idc idc < idc_YYYY-MM-DD.sql`
- **Upgrade**: `git pull`, then re-run the `up -d --build` command; migrations
  apply automatically at backend start.
- **Rollback**: `docker compose -f docker-compose.prod.yml exec backend alembic downgrade -1`
  then start the previous image. Audit events are append-only; never edit them
  to "fix" data.

## 6. Known limits (deliberate)

- **Frontend Entra sign-in is not wired.** The backend fully validates
  bearer tokens today, but the React app still sends the dev `X-User-Email`
  header. Until an MSAL sign-in flow is added to the frontend, production use
  is limited to `IDC_AUTH_MODE=dev` + single trusted user, or API access with
  real tokens. This is the next production-readiness step, and needs the app
  registration to exist first (section 3).
- No TLS termination in this compose file - put the host behind the standard
  CWS reverse proxy / load balancer for HTTPS.
- `exports/` (starter-pack zips) is container-local; export again after a
  container rebuild if a zip is needed.
