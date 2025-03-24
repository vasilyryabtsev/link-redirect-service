from celery import Celery
from celery.schedules import crontab
from src.config import settings

app = Celery(
    "worker",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@rabbitmq:5672",
    include=["src.tasks.tasks"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)

app.conf.beat_schedule = {
    "cleanup-expired-links-every-minute": {
        "task": "src.tasks.tasks.cleanup_expired_links_task",
        "schedule": crontab(minute="*/1"),
    },
    "update-stats-every-five-minute": {
        "task": "src.tasks.tasks.update_stats_task",
        "schedule": crontab(minute="*/1"),
    }
}

if __name__ == '__main__':
    app.start()