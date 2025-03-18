from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, text

from src.users.schemas import UserData, RegUser, Message
from src.database import get_async_session
from src.users.models import User
from src.users.service import get_password_hash

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: RegUser, session: AsyncSession = Depends(get_async_session)) -> Message:
    user_dict = user_data.model_dump()
    query = select(User).where(User.username == user_dict['username'])
    user = await session.execute(query)
    if user.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='This user already exists.'
        )
    statement = insert(User).values({
        "username": user_dict['username'], 
        "hashed_password": get_password_hash(user_dict['password'])
    })
    try:
        await session.execute(statement)
        await session.commit()
        return Message(text='Registration completed!')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
