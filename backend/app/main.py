"""CWS Internal Development Coordinator - FastAPI application.

Modular monolith: one app, one PostgreSQL database, domain packages
under app/. Routers are registered here as tasks land (see
docs/MVP_TASK_PLAN.md).
"""

from fastapi import FastAPI

from app.config import settings
from app.registry.router import router as registry_router
from app.status.router import router as status_router

app = FastAPI(
    title="CWS Internal Development Coordinator",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(registry_router)
app.include_router(status_router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}


# Routers land per task:
# T5: app.docs_matrix.router
# T7/T8: app.starterpack.router
# T9: app.ai.router
