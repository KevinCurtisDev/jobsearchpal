"""Celery app for background and scheduled work. Schedules use Europe/Dublin time.

Run:  celery -A app.workers.celery_app worker -l info
      celery -A app.workers.celery_app beat -l info
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("offerlight", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    timezone="Europe/Dublin",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_time_limit=300,
    task_soft_time_limit=240,
    beat_schedule={
        # Privacy jobs generated from app/privacy/data_inventory.toml (docs/13).
        "privacy-enforce-retention": {
            "task": "app.workers.privacy.enforce_retention",
            "schedule": crontab(hour=2, minute=30),
        },
        "privacy-process-erasures": {
            "task": "app.workers.privacy.process_erasures",
            "schedule": crontab(hour=3, minute=0),
        },
        # Added per stage (docs/12-deployment-and-ops.md §Scheduled jobs), e.g.:
        # "ingest-jobs": {"task": "app.workers.tasks.ingest_jobs",
        #                 "schedule": crontab(hour=1, minute=0)},
    },
)


@celery_app.task(name="app.workers.ping")
def ping() -> str:
    return "pong"


# Register task modules.
import app.workers.privacy_tasks  # noqa: E402, F401
