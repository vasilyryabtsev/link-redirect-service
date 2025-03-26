from typing import Optional, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.users.schemas import UserData
from src.users.service import get_current_active_user_soft, get_current_active_user
from src.database import get_async_session, redis_cache, redis_stats
from src.schemas import Message
from src.config import settings
from src.links.schemas import Url, LinkData, CustomUrl
from src.links.service import (code_to_url,
                               update_link,
                               select_by_link,
                               delete_link,
                               get_link_exists_by_code,
                               get_link_exists_by_link,
                               generate_short_link,
                               get_user_link)


router = APIRouter(prefix='/links', tags=['Link'])

@router.post("/shorten/", status_code=status.HTTP_201_CREATED)
async def create_short_link(
    url: CustomUrl,
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[UserData] = Depends(get_current_active_user_soft)
) -> Url:
    """
    Создает сокращенную версию длинной URL-ссылки.

    Args:
        url: Объект с оригинальным URL и дополнительными параметрами.
        session: Асинхронная сессия SQLAlchemy.
        current_user: Данные текущего пользователя (опционально).

    Returns:
        Объект с сокращенной версией URL.

    Raises:
        HTTPException: 208 если ссылка уже имеет сокращенную версию.
    """
    link_dict = url.model_dump()
    link_old = await select_by_link(link_dict['link'], session)
    if link_old:
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail=f'This link already has a short version: {code_to_url(link_old.code)}'
        )
    if current_user:
        link_dict['owner'] = current_user.model_dump()['username']
    code = await generate_short_link(session=session, **link_dict)
    return Url(link=code_to_url(code))

@router.get("/{short_code}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_to_original_link(
    short_code: str,
    session: AsyncSession = Depends(get_async_session)
) -> RedirectResponse:
    """
    Перенаправляет по сокращенной ссылке на оригинальный URL.

    Args:
        short_code: Уникальный код сокращенной ссылки.
        session: Асинхронная сессия SQLAlchemy.

    Returns:
        RedirectResponse: Перенаправление на оригинальный URL.

    Notes:
        - Использует Redis для кэширования
        - Обновляет счетчик переходов и дату последнего использования,
          если ссылка не найдена в кэше
    """
    cached_link = redis_cache.get(short_code)
    if cached_link is not None:
        cached_link = cached_link.decode('utf-8')
        redis_stats.zincrby("link_stats", 1, short_code)
        return RedirectResponse(url=cached_link)
    link = await get_link_exists_by_code(session, short_code)
    redis_cache.set(short_code, link.link, ex=settings.REDIS_CACHE_EXPIRATION)
    values = {
        "updated_at": datetime.now(),
        "usage_count": link.usage_count + 1
    }
    await update_link(session, link.id, values)
    return RedirectResponse(url=link.link)

@router.delete("/{short_code}", status_code=status.HTTP_200_OK)
async def delete_short_link(
    short_code: str,
    current_user: Annotated[UserData, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_async_session)
) -> Message:
    """
    Удаляет сокращенную ссылку.

    Args:
        short_code: Уникальный код сокращенной ссылки.
        current_user: Данные аутентифицированного пользователя.
        session: Асинхронная сессия SQLAlchemy.

    Returns:
        Сообщение об успешном удалении.

    Notes:
        - Доступно только владельцу ссылки
        - Удаляет как саму ссылку, так и связанные статистические данные
    """
    link = await get_user_link(session, current_user, short_code)
    await delete_link(session, link.id)
    return Message(message=f"{code_to_url(link.code)} has been removed.")

@router.put("/{short_code}", status_code=status.HTTP_200_OK)
async def update_short_link(
    short_code: str,
    current_user: Annotated[UserData, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_async_session)
) -> Url:
    """
    Обновляет (пересоздает) сокращенную ссылку.

    Args:
        short_code: Уникальный код сокращенной ссылки.
        current_user: Данные аутентифицированного пользователя.
        session: Асинхронная сессия SQLAlchemy.

    Returns:
        Новый сокращенный URL.

    Notes:
        - Фактически создает новую ссылку с тем же оригинальным URL
        - Сохраняет параметры оригинальной ссылки (expires_at и владельца)
    """
    link = await get_user_link(session, current_user, short_code)
    await delete_link(session, link.id)
    code = await generate_short_link(session=session,
                                     link=link.link,
                                     expires_at=link.expires_at,
                                     owner=link.owner)
    return Url(link=code_to_url(code))

@router.get("/{short_code}/stats", status_code=status.HTTP_200_OK)
async def get_short_link_stats(
    short_code: str,
    session: AsyncSession = Depends(get_async_session)
) -> LinkData:
    """
    Возвращает статистику по сокращенной ссылке.

    Args:
        short_code: Уникальный код сокращенной ссылки.
        session: Асинхронная сессия SQLAlchemy.

    Returns:
        Данные ссылки.
    """
    link = await get_link_exists_by_code(session, short_code)
    return LinkData(
        link=link.link,
        code=link.code,
        created_at=link.created_at,
        usage_count=link.usage_count,
        updated_at=link.updated_at
    )

@router.get("/search/", status_code=status.HTTP_200_OK)
async def search_link(
    original_url: str,
    session: AsyncSession = Depends(get_async_session)
) -> Url:
    """
    Ищет сокращенную версию по оригинальному URL.

    Args:
        original_url: Полный оригинальный URL для поиска.
        session: Асинхронная сессия SQLAlchemy.

    Returns:
        Сокращенная версия URL, если найдена.

    Notes:
        - Поиск происходит по точному совпадению URL
    """
    link = await get_link_exists_by_link(session, original_url)
    return Url(link=code_to_url(link.code))
