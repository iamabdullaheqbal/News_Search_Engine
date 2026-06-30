from celery import Celery
from celery.schedules import crontab
from app.core.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "veritas",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.ingestion_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "ingest-articles-every-6-hours": {
            "task": "app.tasks.ingestion_tasks.run_ingestion_task",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)
