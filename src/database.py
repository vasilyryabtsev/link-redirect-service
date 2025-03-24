import redis

from typing import Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column
from sqlalchemy.types import String, Integer

from src.config import get_db_url


DATABASE_URL = get_db_url()
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
    
int_pk = Annotated[int, mapped_column(Integer, primary_key=True)]
str_uniq = Annotated[str, mapped_column(String, unique=True, nullable=False)]

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

redis_cache = redis.Redis(host='redis_app', port=6379, db=0)
redis_stats = redis.Redis(host='redis_app', port=6379, db=1)