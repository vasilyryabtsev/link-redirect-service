from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from fastapi import status, HTTPException
from datetime import datetime

from src.links.models import Link
from src.users.schemas import UserData
from src.config import settings, sqids, timezone


def get_code(link_id: int) -> str:
    """
    Генерирует уникальный код ссылки на основе ID.

    Args:
        link_id: Идентификатор ссылки в базе данных.

    Returns:
        Уникальный закодированный код ссылки.

    Note:
        Использует настройки LINK_ENCODING_SIZE для определения длины кода.
    """
    return sqids.encode(list(range(link_id, link_id + settings.LINK_ENCODING_SIZE)))

def code_to_url(code: str) -> str:
    """
    Формирует полный URL сокращенной ссылки.

    Args:
        code: Уникальный код ссылки.

    Returns:
        Полный URL вида 'http://host:port/links/{code}'.
    """
    return f"http://{settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}/links/{code}"

async def select_by_link(link: str, session: AsyncSession) -> (Link | None):
    query = select(Link).where(Link.link == link)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def select_by_code(code: str, session: AsyncSession) -> (Link | None):
    """
    Ищет ссылку в базе данных по коду сокращения.

    Args:
        code: Код сокращенной ссылки.
        session: Асинхронная сессия базы данных.

    Returns:
        Объект Link или None, если ссылка не найдена.
    """
    query = select(Link).where(Link.code == code)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def insert_link(
    session: AsyncSession, 
    values_dict: dict
) -> None:
    """
    Добавляет новую ссылку в базу данных.

    Args:
        session: Асинхронная сессия базы данных.
        values_dict: Словарь с данными для вставки.

    Raises:
        HTTPException: 500 при ошибке вставки.
    """
    statement = insert(Link).values(values_dict)
    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_link(session: AsyncSession, id: int, values: dict) -> None:
    """
    Обновляет данные ссылки в базе данных.

    Args:
        session: Асинхронная сессия базы данных.
        id: Идентификатор обновляемой ссылки.
        values: Словарь с новыми значениями полей.

    Raises:
        HTTPException: 500 при ошибке обновления.
    """
    statement = update(Link).where(Link.id == id).values(values)
    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def delete_link(session: AsyncSession, id: int) -> None:
    """
    Удаляет ссылку из базы данных.

    Args:
        session: Асинхронная сессия базы данных.
        id: Идентификатор удаляемой ссылки.

    Raises:
        HTTPException: 500 при ошибке удаления.
    """
    statement = delete(Link).where(Link.id == id)
    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
async def generate_short_link(
    session: AsyncSession, 
    link: str,
    expires_at: datetime,
    owner: str | None = None,
    custom_alias: str | None = None
) -> str:
    """
    Генерирует короткую ссылку и сохраняет её в базу данных.

    Args:
        session: Асинхронная сессия базы данных.
        link: Оригинальный URL для сокращения.
        expires_at: Дата истечения срока действия.
        owner: Владелец ссылки (опционально).
        custom_alias: Пользовательский алиас (опционально).

    Returns:
        Сгенерированный код сокращенной ссылки.

    Raises:
        HTTPException: 409 если пользовательский алиас уже занят.
    """
    await insert_link(session, {"link": link,
                                "created_at": datetime.now(timezone),
                                "updated_at": datetime.now(timezone),
                                "expires_at": expires_at,
                                "owner": owner})
    link_new = await select_by_link(link, session)
    if custom_alias is None:
        code = get_code(link_new.id)
    else:
        link_alias = await select_by_code(custom_alias, session)
        if link_alias:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This alias is already taken."
            )
        code = custom_alias
    await update_link(session, link_new.id, {"code": code,
                                             "updated_at": datetime.now(timezone)})
    return code

async def get_link_exists_by_code(session: AsyncSession, short_code: str) -> Link:
    """
    Проверяет существование ссылки по коду.

    Args:
        session: Асинхронная сессия базы данных.
        short_code: Код сокращенной ссылки.

    Returns:
        Объект Link.

    Raises:
        HTTPException: 404 если ссылка не найдена.
    """
    link = await select_by_code(short_code, session)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This link doesn't exist."
        )
    return link

async def get_link_exists_by_link(session: AsyncSession, link: str) -> Link:
    """
    Проверяет существование ссылки по оригинальному URL.

    Args:
        session: Асинхронная сессия базы данных.
        link: Оригинальный URL.

    Returns:
        Объект Link.

    Raises:
        HTTPException: 404 если ссылка не найдена.
    """
    link = await select_by_link(link, session)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This link doesn't exist."
        )
    return link

async def get_user_link(
    session: AsyncSession,
    current_user: UserData,
    short_code: str
) -> Link:
    """
    Проверяет принадлежность ссылки пользователю.

    Args:
        session: Асинхронная сессия базы данных.
        current_user: Данные текущего пользователя.
        short_code: Код сокращенной ссылки.

    Returns:
        Объект Link.

    Raises:
        HTTPException: 405 если пользователь не владелец.
    """
    link = await get_link_exists_by_code(session, short_code)
    if link.owner != current_user.model_dump()['username']:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"You are not the owner of {code_to_url(link.code)}."
        )
    return link