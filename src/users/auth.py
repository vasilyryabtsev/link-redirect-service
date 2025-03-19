from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, text
from datetime import timedelta

from src.users.schemas import RegUser, Message, Token, UserData
from src.database import get_async_session
from src.users.models import User
from src.users.service import get_password_hash, get_user, authenticate_user, create_access_token, get_current_active_user, get_current_user
from src.config import settings


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: RegUser, session: AsyncSession = Depends(get_async_session)) -> Message:
    user_dict = user_data.model_dump()
    user = await get_user(user_dict['username'], session)
    if user:
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

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/users/me/", response_model=UserData)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
