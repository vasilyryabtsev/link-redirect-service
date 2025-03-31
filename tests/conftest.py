import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import settings

DATABASE_TEST_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

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
