from celery import Celery
from celery.schedules import crontab

from src.config import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "worker",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@rabbitmq:5672",  # URL для подключения к RabbitMQ
    include=["src.tasks"],  # Указываем, где искать задачи
)

# Настройки Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)

# Периодические задачи (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-expired-links-every-30-minutes": {
        "task": "src.tasks.cleanup_expired_links_task",  # Имя задачи
        "schedule": crontab(minute="*/1"),  # Каждые 30 минут
    },
}