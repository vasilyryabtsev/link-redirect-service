import jwt

from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from datetime import datetime, timedelta, timezone

from src.config import pwd_context, settings
from src.users.models import User
from src.users.schemas import TokenData, UserData
from src.database import get_async_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_user(username: str, session: AsyncSession) -> (User | None):
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none()
    
async def authenticate_user(username: str, password: str, session: AsyncSession) -> (User | bool):
    user = await get_user(username, session)
    if user is None:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> (UserData | None):
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
) -> UserData:
    try:
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    except AttributeError:
        raise credentials_exception
    
async def get_current_active_user_soft(
    current_user: Annotated[UserData, Depends(get_current_user)],
) -> (UserData | None):
    try:
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    except AttributeError:
        return None

async def insert_user(username: str, hashed_password: str, session: AsyncSession) -> None:
    statement = insert(User).values({
        "username": username, 
        "hashed_password": hashed_password
    })
    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
