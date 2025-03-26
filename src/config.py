import os
import pytz

from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext
from sqids import Sqids


class Settings(BaseSettings):
    """Класс конфигурации приложения, загружающий настройки из .env файла.

    Содержит все необходимые настройки для работы приложения:
    - Параметры подключения к БД (PostgreSQL)
    - Параметры подключения к Redis
    - Параметры подключения к RabbitMQ
    - Настройки FastAPI сервера
    - Настройки аутентификации и безопасности
    - Параметры работы с ссылками
    - Таймзона и расписание задач

    Атрибуты:
        DB_USER: Логин для подключения к PostgreSQL
        DB_PASS: Пароль для подключения к PostgreSQL
        DB_HOST: Хост PostgreSQL
        DB_PORT: Порт PostgreSQL
        DB_NAME: Имя базы данных
        REDIS_HOST: Хост Redis
        REDIS_PORT: Порт Redis
        REDIS_CACHE_EXPIRATION: Время жизни кэша в секундах
        RABBITMQ_HOST: Хост RabbitMQ
        RABBITMQ_PORT: Порт RabbitMQ
        RABBITMQ_USER: Логин RabbitMQ
        RABBITMQ_PASS: Пароль RabbitMQ
        FASTAPI_HOST: Хост FastAPI сервера
        FASTAPI_PORT: Порт FastAPI сервера
        SECRET_KEY: Секретный ключ для JWT
        ALGORITHM: Алгоритм шифрования JWT
        ACCESS_TOKEN_EXPIRES_MINUTES: Время жизни токена в минутах
        LINK_ENCODING_SIZE: Размер кодирования ссылок
        TIMEZONE: Часовой пояс сервера
        CLEAN_UP_EXPIRED_LINKS_TIME: Периодичность очистки ссылок (сек)
        UPDATE_STATS_TIME: Периодичность обновления статистики (сек)
    """
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_CACHE_EXPIRATION: int
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    FASTAPI_HOST: str
    FASTAPI_PORT: int
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    LINK_ENCODING_SIZE: int
    TIMEZONE: str
    CLEAN_UP_EXPIRED_LINKS_TIME: int
    UPDATE_STATS_TIME: int
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

sqids = Sqids()

timezone = pytz.timezone(settings.TIMEZONE)

def get_db_url() -> str:
    """
    Формирует URL для подключения к PostgreSQL базе данных.
    
    Использует настройки из конфига для формирования строки подключения
    в формате postgresql+asyncpg.

    Возвращает:
        str: Строка подключения к базе данных
    """
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
