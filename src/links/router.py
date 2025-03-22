from typing import Optional, Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.users.schemas import UserData
from src.users.service import get_current_active_user_soft, get_current_active_user
from src.database import get_async_session
from src.schemas import Message
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
    link = await get_link_exists_by_code(session, short_code)
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
    link = await get_user_link(session, current_user, short_code)
    await delete_link(session, link.id)
    return Message(message=f"{code_to_url(link.code)} has been removed.")

@router.put("/{short_code}", status_code=status.HTTP_200_OK)
async def update_short_link(
    short_code: str,
    current_user: Annotated[UserData, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_async_session)
) -> Url:
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
    link = await get_link_exists_by_link(session, original_url)
    return Url(link=code_to_url(link.code))
