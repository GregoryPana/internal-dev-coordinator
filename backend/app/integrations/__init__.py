"""In-app integration settings (2026-07-14 direction).

Lets an admin configure external integrations (starting with GitHub read)
inside the application instead of env files: credentials are stored
encrypted at rest (Fernet, key = IDC_SECRET_KEY), never echoed back to any
client, and every change is audited. Env-file values remain the fallback
when no DB row exists, so nothing breaks for env-configured deployments.
"""
