from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from src.links.service import get_code
from src.links.schemas import NewLink
from src.users.schemas import UserData
from src.users.service import get_current_active_user_soft
from src.database import get_async_session
from src.links.models import Link

router = APIRouter(prefix='/links', tags=['Link'])

@router.post("/shorten/", status_code=status.HTTP_201_CREATED)
async def read_users_me(
    link: NewLink,
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[UserData] = Depends(get_current_active_user_soft)
):
    link_data = link.model_dump()
    if current_user:
        link_data['owner'] = current_user.model_dump()['username']
    link_data['code'] =  get_code(link_data['link'])
    statement = insert(Link).values(link_data)
    try:
        await session.execute(statement)
        await session.commit()
        return {"text": f"Your short link: {link_data['code']}"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))    
