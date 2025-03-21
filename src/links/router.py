from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.links.service import get_code, get_link, insert_link, update_link
from src.links.schemas import NewLink
from src.users.schemas import UserData
from src.users.service import get_current_active_user_soft
from src.database import get_async_session
from src.schemas import Message


router = APIRouter(prefix='/links', tags=['Link'])

@router.post("/shorten/", status_code=status.HTTP_201_CREATED)
async def read_users_me(
    link_data: NewLink,
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[UserData] = Depends(get_current_active_user_soft)
) -> Message:
    link_dict = link_data.model_dump()
    link_old = await get_link(link_dict['link'], session)
    if link_old:
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail=f'This link already has a short version: {link_old.code}'
        )
    if current_user:
        link_dict['owner'] = current_user.model_dump()['username']
    await insert_link(session, **link_dict)
    link_new = await get_link(link_dict['link'], session)
    code = get_code(link_new.id)
    await update_link(session, link_new.id, code)
    return Message(message=f"Your short link: {code}")
