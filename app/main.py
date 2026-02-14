import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes import router
from app.database import SessionLocal

app = FastAPI(title="OOB Governance MVP")
app.include_router(router)

scheduler = BackgroundScheduler(timezone="UTC")


logger = logging.getLogger(__name__)


def scheduled_heartbeat():
    logger.info("scheduler_heartbeat")


def _scheduler_lock_acquired() -> bool:
    db = SessionLocal()
    try:
        acquired = db.execute(text("SELECT pg_try_advisory_lock(987654321)")).scalar()
        db.commit()
        return bool(acquired)
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    if os.getenv("ENABLE_SCHEDULER", "true").lower() != "true":
        logger.info("Scheduler disabled by ENABLE_SCHEDULER")
        return

    if not _scheduler_lock_acquired():
        logger.info("Scheduler lock not acquired; skipping scheduler start")
        return

    if not scheduler.running:
        scheduler.add_job(scheduled_heartbeat, "interval", minutes=5, id="heartbeat", replace_existing=True)
        scheduler.start()
        logger.info("Scheduler started")


@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown(wait=False)
