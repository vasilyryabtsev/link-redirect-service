import os
import pytz

from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext
from sqids import Sqids


class Settings(BaseSettings):
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
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
