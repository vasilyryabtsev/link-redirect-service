import logging
import asyncio

from sqlalchemy import select, delete, insert
from datetime import datetime
from celery import shared_task

from src.database import get_async_session
from src.links.models import Link
from src.archive.models import ArchivedLink
from src.config import timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clean_up_expired_links():
    async for session in get_async_session():
        query = select(Link).where(Link.expires_at < datetime.now(timezone))
        result = await session.execute(query)
        for item in result.scalars():
            values_dict = {
                "owner": item.owner,
                "link": item.link,
                "code": item.code,
                "created_at": item.created_at,
                "deleted_at": datetime.now(timezone),
                "usage_count": item.usage_count
            }
            statement = insert(ArchivedLink).values(values_dict)
            try:
                await session.execute(statement)
                await session.commit()
                logger.info("Expired link successfully saved in archive.")
            except Exception as e:
                logger.error(f"Error saving link to archive: {e}")
                
            statement = delete(Link).where(Link.id == item.id)
            try:
                await session.execute(statement)
                await session.commit()
                logger.info("Expired link deleted successfully.")
            except Exception as e:
                logger.error(f"Error deleting a link: {e}")

@shared_task
def cleanup_expired_links_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(clean_up_expired_links())
