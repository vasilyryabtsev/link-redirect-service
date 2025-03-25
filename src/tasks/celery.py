from celery import Celery
from celery.schedules import crontab
from src.config import settings

app = Celery(
    "worker",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}",
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
        "schedule": crontab(minute=f"*/{settings.CLEAN_UP_EXPIRED_LINKS_TIME}"),
    },
    "update-stats-every-five-minute": {
        "task": "src.tasks.tasks.update_stats_task",
        "schedule": crontab(minute=f"*/{settings.UPDATE_STATS_TIME}"),
    }
}

if __name__ == '__main__':
    app.start()