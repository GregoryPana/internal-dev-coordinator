"""CWS Internal Development Coordinator - FastAPI application.

Modular monolith: one app, one PostgreSQL database, domain packages
under app/. Routers are registered here as tasks land (see
docs/MVP_TASK_PLAN.md).
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.ai.router import router as ai_router
from app.audit.router import router as audit_router
from app.config import settings
from app.docs_matrix.router import router as docs_matrix_router
from app.integrations.router import router as integrations_router
from app.registry.router import router as registry_router
from app.repo.poller import poller_loop
from app.repo.router import router as repo_router
from app.starterpack.router import router as starterpack_router
from app.status.router import router as status_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = None
    if settings.enable_background_polling:
        task = asyncio.create_task(poller_loop())
    yield
    if task is not None:
        task.cancel()


app = FastAPI(
    title="CWS Internal Development Coordinator",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.include_router(registry_router)
app.include_router(status_router)
app.include_router(docs_matrix_router)
app.include_router(starterpack_router)
app.include_router(ai_router)
app.include_router(audit_router)
app.include_router(repo_router)
app.include_router(integrations_router)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.environment,
        "edition": settings.edition,
    }
