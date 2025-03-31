import os
import pytest_asyncio

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_TEST_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(DATABASE_TEST_URL, echo=True)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
    connection = await db_engine.connect()
    transaction = await connection.begin()
    SessionLocal = async_sessionmaker(bind=connection, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()
