import jwt

from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from datetime import datetime, timedelta, timezone

from src.config import pwd_context, settings
from src.users.models import User
from src.users.schemas import TokenData, UserData, UserInDB
from src.database import get_async_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str, session: AsyncSession):
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none()
    
async def authenticate_user(username: str, password: str, session: AsyncSession):
    user = await get_user(username, session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        return None
    async for session in get_async_session():
        user = await get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return UserData(username=user.username, disabled=user.disabled)

async def get_current_active_user(
    current_user: Annotated[UserData, Depends(get_current_user)],
):
    try:
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    except AttributeError:
        raise credentials_exception
    
async def get_current_active_user_soft(
    current_user: Annotated[UserData, Depends(get_current_user)],
):
    try:
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    except AttributeError:
        return None
