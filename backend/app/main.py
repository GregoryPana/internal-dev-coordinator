"""CWS Internal Development Coordinator - FastAPI application.

Modular monolith: one app, one PostgreSQL database, domain packages
under app/. Routers are registered here as tasks land (see
docs/MVP_TASK_PLAN.md).
"""

from fastapi import FastAPI

from app.ai.router import router as ai_router
from app.audit.router import router as audit_router
from app.config import settings
from app.docs_matrix.router import router as docs_matrix_router
from app.registry.router import router as registry_router
from app.starterpack.router import router as starterpack_router
from app.status.router import router as status_router

app = FastAPI(
    title="CWS Internal Development Coordinator",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(registry_router)
app.include_router(status_router)
app.include_router(docs_matrix_router)
app.include_router(starterpack_router)
app.include_router(ai_router)
app.include_router(audit_router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}
