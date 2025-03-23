import logging
import asyncio

from sqlalchemy import delete
from datetime import datetime
from celery import shared_task

from src.database import get_async_session
from src.links.models import Link
from src.config import timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clean_up_expired_links():
    async for session in get_async_session():
        statement = delete(Link).where(Link.expires_at < datetime.now(timezone))
        try:
            await session.execute(statement)
            await session.commit()
            logger.info("Expired links cleaned up successfully.")
        except Exception as e:
            logger.error(f"Error cleaning up expired links: {e}")

@shared_task
def cleanup_expired_links_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(clean_up_expired_links())