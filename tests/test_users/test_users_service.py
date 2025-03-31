import pytest
import pytest_asyncio

from sqlalchemy import select
from datetime import timedelta
from jwt.exceptions import InvalidTokenError

from tests.conftest import db_session
from test_users.test_users_models import valid_user

from src.users.models import User
from src.users.service import (verify_password,
                               get_password_hash,
                               get_user,
                               authenticate_user,
                               create_access_token,
                               get_current_user,
                               get_current_active_user,
                               get_current_active_user_soft,
                               insert_user)


async def add_user(session, user):
    session.add(user)
    await session.commit()

def test_get_password_hash():
    assert isinstance(get_password_hash("password"), str)

@pytest.mark.parametrize("plain_password, hashed_password, expected", [
    ("password", get_password_hash("password"), True),
    ("wrong_password", get_password_hash("password"), False)
])
def test_verify_password(plain_password, hashed_password, expected):
    assert verify_password(plain_password, hashed_password) == expected

@pytest.mark.asyncio
async def test_get_user(db_session, valid_user):
    await add_user(db_session, valid_user)
    user = await get_user(valid_user.username, db_session)
    assert user.username == valid_user.username
    
@pytest.mark.asyncio
async def test_get_user_none(db_session, valid_user):
    user = await get_user(valid_user.username, db_session)
    assert user is None

@pytest.mark.asyncio
async def test_authenticate_user_not_found(db_session, valid_user):
    user = await authenticate_user(
        valid_user.username,
        "password",
        db_session
    )
    assert user == False
    
@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session, valid_user):
    await add_user(db_session, valid_user)
    user = await authenticate_user(
        valid_user.username,
        "wrong_password",
        db_session
    )
    assert user == False

@pytest.mark.asyncio
async def test_authenticate_user(db_session, valid_user):
    await add_user(db_session, valid_user)
    user = await authenticate_user(
        valid_user.username,
        "password",
        db_session
    )
    assert user.username == valid_user.username

@pytest.mark.parametrize("expires_delta", [None, timedelta(minutes=15)])
def test_create_access_token(valid_user, expires_delta):
    token = create_access_token(
        data={"sub": valid_user.username},
        expires_delta=expires_delta
    )
    assert isinstance(token, str)

@pytest.mark.asyncio
async def test_get_current_user_none_user(valid_user):
    token = create_access_token(data={"sub": valid_user.username})
    with pytest.raises(Exception):
        await get_current_user(token)

@pytest.mark.asyncio
async def test_insert_user(db_session, valid_user):
    await insert_user(
        username=valid_user.username,
        hashed_password=valid_user.hashed_password,
        session=db_session
    )
    query = select(User).where(User.username == valid_user.username)
    result = await db_session.execute(query)
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.username == valid_user.username
    
@pytest.mark.asyncio
async def test_get_current_user_raise_exception(db_session, valid_user):
    await insert_user(
        username=valid_user.username,
        hashed_password=valid_user.hashed_password,
        session=db_session
    )
    with pytest.raises(Exception):
        await insert_user(
            username=valid_user.username,
            hashed_password=valid_user.hashed_password,
            session=db_session
        )