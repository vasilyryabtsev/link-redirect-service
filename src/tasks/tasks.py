import logging
import asyncio

from datetime import datetime
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert

from src.database import get_async_session, redis_stats
from src.links.models import Link
from src.links.service import get_link_exists_by_code, update_link
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
            
            try:
                # Архивируем ссылку
                await session.execute(insert(ArchivedLink).values(values_dict))
                # Удаляем оригинальную ссылку
                await session.execute(delete(Link).where(Link.id == item.id))
                await session.commit()
                logger.info(f"Link {item.code} archived and deleted successfully.")
            except Exception as e:
                logger.error(f"Error processing link {item.code}: {e}")
                await session.rollback()
        return {'expired links': [item.link for item in result.scalars().fetchall()]}

@shared_task(name='src.tasks.tasks.cleanup_expired_links_task')
def cleanup_expired_links_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(clean_up_expired_links())
    
async def update_stats():
    async for session in get_async_session():
        # Получаем всю статистику из Redis
        stats = redis_stats.zrange("link_stats", 0, -1, withscores=True)
        print(stats)
        if stats:
            for short_code, count in stats:
                # Получаем ссылку из БД
                link = await get_link_exists_by_code(session, short_code.decode('utf-8'))
                if link:
                    values = {
                        "updated_at": datetime.now(),
                        "usage_count": link.usage_count + int(count)
                    }
                    await update_link(session, link.id, values)
            
            # Очищаем статистику после синхронизации
            redis_stats.delete("link_stats")
    return {'cached links stats:': stats}

@shared_task(name='src.tasks.tasks.update_stats_task')
def cleanup_expired_links_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_stats())