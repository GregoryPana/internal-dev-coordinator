"""CWS Internal Development Coordinator - FastAPI application.

Modular monolith: one app, one PostgreSQL database, domain packages
under app/. Routers are registered here as tasks land (see
docs/MVP_TASK_PLAN.md).
"""

from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title="CWS Internal Development Coordinator",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}


# Routers land per task:
# T3: app.registry.router
# T4: app.status.router
# T5: app.docs_matrix.router
# T7/T8: app.starterpack.router
# T9: app.ai.router
