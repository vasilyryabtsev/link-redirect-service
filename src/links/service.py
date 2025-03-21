from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from fastapi import status, HTTPException

from src.links.models import Link
from src.config import settings, sqids


def get_code(link_id: int) -> str:
    return sqids.encode(list(range(link_id, link_id + settings.LINK_ENCODING_SIZE)))

async def get_link(link: str, session: AsyncSession) -> (Link | None):
    query = select(Link).where(Link.link == link)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def insert_link(session: AsyncSession, link: str, owner: str | None = None) -> None:
    statement = insert(Link).values(link=link, owner=owner)
    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_link(session: AsyncSession, id: int, code: str) -> None:
    statement = update(Link).where(Link.id == id).values(code=code)
    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
