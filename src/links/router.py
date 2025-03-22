from typing import Optional, Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.users.schemas import UserData
from src.users.models import User
from src.users.service import get_current_active_user_soft, get_current_active_user
from src.database import get_async_session
from src.schemas import Message
from src.config import URL
from src.links.schemas import NewLink
from src.links.service import (get_code, 
                               insert_link, 
                               update_link,
                               select_by_link,
                               select_by_code,
                               delete_link)


router = APIRouter(prefix='/links', tags=['Link'])

@router.post("/shorten/", status_code=status.HTTP_201_CREATED)
async def create_short_link(
    link_data: NewLink,
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[UserData] = Depends(get_current_active_user_soft)
) -> Message:
    link_dict = link_data.model_dump()
    link_old = await select_by_link(link_dict['link'], session)
    if link_old:
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail=f'This link already has a short version: {link_old.code}'
        )
    if current_user:
        link_dict['owner'] = current_user.model_dump()['username']
    await insert_link(session, **link_dict)
    link_new = await select_by_link(link_dict['link'], session)
    code = get_code(link_new.id)
    await update_link(session, link_new.id, {"code": code})
    return Message(message=f"Your short link: {URL}/links/{code}")

@router.get("/{short_code}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_to_original_link(
    short_code: str,
    session: AsyncSession = Depends(get_async_session)
) -> RedirectResponse:
    link = await select_by_code(short_code, session)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This link doesn't exist."
        )
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
    link = await select_by_code(short_code, session)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This link doesn't exist."
        )
    if link.owner == current_user.model_dump()['username']:
        await delete_link(session, link.id)
        return Message(message=f"Short link for {link.link} removed.")
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=f"You are not the owner of {URL}/links/{link.code}."
    )
