from celery import Celery
from celery.schedules import crontab

from src.config import settings


celery_app = Celery(
    "worker",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@rabbitmq:5672",
    include=["src.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "cleanup-expired-links-every-minute": {
        "task": "src.tasks.cleanup_expired_links_task",
        "schedule": crontab(minute="*/1"),
    },
}