"""Background repo-tracking loop, started from the FastAPI lifespan.

Runs poll_all_projects() every IDC_REPO_POLL_INTERVAL_MINUTES while the
GitHub integration is enabled (in-app setting or env). Failures are logged
and never crash the loop - the next tick simply tries again. Disabled
entirely by IDC_ENABLE_BACKGROUND_POLLING=false (tests force this off).
"""

import asyncio
import logging

from app.config import settings
from app.db import SessionLocal

logger = logging.getLogger("idc.repo.poller")


def run_poll_once() -> None:
    """One synchronous tracking pass with its own session (also usable from
    a shell/cron: python -c "from app.repo.poller import run_poll_once; run_poll_once()")."""
    from app.integrations import service as integrations_service
    from app.repo import service as repo_service

    db = SessionLocal()
    try:
        if not integrations_service.resolve_github(db).enabled:
            logger.debug("repo poll skipped: GitHub integration disabled")
            return
        summary = repo_service.poll_all_projects(db)
        logger.info(
            "repo poll: %d polled, %d ok, %d failed, %d without repo%s",
            summary.polled,
            summary.succeeded,
            summary.failed,
            summary.skipped_no_repo,
            f" ({'; '.join(summary.errors)})" if summary.errors else "",
        )
    finally:
        db.close()


async def poller_loop() -> None:
    interval = max(1, settings.repo_poll_interval_minutes) * 60
    while True:
        try:
            await asyncio.to_thread(run_poll_once)
        except Exception:  # never let one bad pass kill the loop
            logger.exception("repo poll pass failed")
        await asyncio.sleep(interval)
