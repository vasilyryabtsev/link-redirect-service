import pytest

from sqlalchemy import select

from tests.conftest import db_session
from test_links.test_links_models import valid_link

from src.config import settings
from src.users.models import User
from src.users.schemas import UserData
from src.links.models import Link
from src.links.service import (get_code, 
                               code_to_url,
                               select_by_link,
                               select_by_code,
                               insert_link,
                               update_link,
                               delete_link,
                               generate_short_link,
                               get_link_exists_by_code,
                               get_link_exists_by_link,
                               get_user_link)

async def add_valid_link(session, link):
    session.add(link)
    await session.commit()
    
def get_values(link: Link) -> dict:
    return {
        "owner": link.owner,
        "link": link.link,
        "code": link.code,
        "created_at": link.created_at,
        "updated_at": link.updated_at,
        "usage_count": link.usage_count,
        "expires_at": link.expires_at
    }
    
async def select_valid_link_or_none(session, link):
    query = select(Link).where(Link.link == link.link)
    res = await session.execute(query)
    return res.scalar_one_or_none()

def test_get_code():
    assert isinstance(get_code(1), str)

def test_get_code_url():
    code = get_code(1)
    assert code_to_url(code) == f"http://{settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}/links/{code}"

@pytest.mark.asyncio
async def test_select_by_link_none(db_session, valid_link):
    link = await select_by_link(valid_link.link, db_session)
    assert link is None

@pytest.mark.asyncio
async def test_select_by_link(db_session, valid_link):
    await add_valid_link(db_session, valid_link)
    res = await select_by_link(valid_link.link, db_session)
    assert valid_link.link == res.link

@pytest.mark.asyncio
async def test_select_by_code_none(db_session, valid_link):
    link = await select_by_code(valid_link.code, db_session)
    assert link is None
    
@pytest.mark.asyncio
async def test_select_by_code(db_session, valid_link):
    await add_valid_link(db_session, valid_link)
    res = await select_by_code(valid_link.code, db_session)
    assert valid_link.link == res.link

@pytest.mark.asyncio
async def test_insert_link(db_session, valid_link):
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link is None
    values = get_values(valid_link)
    await insert_link(db_session, values)
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link.link == valid_link.link

@pytest.mark.asyncio
async def test_insert_link_raise_exception(db_session):
    with pytest.raises(Exception):
        await insert_link(db_session, Link())

@pytest.mark.asyncio
async def test_update_link(db_session, valid_link):
    await add_valid_link(db_session, valid_link)
    link = await select_valid_link_or_none(db_session, valid_link)
    await update_link(db_session, link.id, {"code": "new_code"})
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link.code == "new_code"

@pytest.mark.asyncio
async def test_update_link_raise_exception(db_session):
    with pytest.raises(Exception):
        await update_link(db_session, 0, {})
        
@pytest.mark.asyncio
async def test_delete_link(db_session, valid_link):
    await add_valid_link(db_session, valid_link)
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link is not None
    await delete_link(db_session, link.id)
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link is None
    
@pytest.mark.asyncio
async def test_delete_link_raise_exception(db_session):
    with pytest.raises(Exception):
        await delete_link(db_session, 'id')

@pytest.mark.asyncio
async def test_generate_short_link_code(db_session, valid_link):
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link is None
    code = await generate_short_link(
        session=db_session,
        link=valid_link.link,
        expires_at=valid_link.expires_at
    )
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link.link == valid_link.link
    assert link.code == code
    
@pytest.mark.asyncio
async def test_generate_short_link_custom_alias(db_session, valid_link):
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link is None
    code = await generate_short_link(
        session=db_session,
        link=valid_link.link,
        expires_at=valid_link.expires_at,
        custom_alias=valid_link.code
    )
    link = await select_valid_link_or_none(db_session, valid_link)
    assert link.link == valid_link.link
    assert link.code == valid_link.code
    assert link.code == code
    
@pytest.mark.asyncio
async def test_generate_short_link_raise_exception(db_session, valid_link):
    await add_valid_link(db_session, valid_link)
    with pytest.raises(Exception):
        await generate_short_link(
            session=db_session,
            link=valid_link.link,
            expires_at=valid_link.expires_at,
            custom_alias=valid_link.code
        )

@pytest.mark.asyncio
async def test_get_link_exists_by_code(db_session, valid_link):
    await add_valid_link(db_session, valid_link)
    link = await get_link_exists_by_code(db_session, valid_link.code)
    assert link.link == valid_link.link

@pytest.mark.asyncio
async def test_get_link_exists_by_code_raise_exception(db_session, valid_link):
    with pytest.raises(Exception):
        await get_link_exists_by_code(db_session, 'code')

@pytest.mark.asyncio
async def test_get_link_exists_by_link(db_session, valid_link):
    await add_valid_link(db_session, valid_link)
    link = await get_link_exists_by_link(db_session, valid_link.link)
    assert link.link == valid_link.link
    
@pytest.mark.asyncio
async def test_get_link_exists_by_link_raise_exception(db_session):
    with pytest.raises(Exception):
        await get_link_exists_by_link(db_session, 'link')

@pytest.mark.asyncio
async def test_get_user_link(db_session, valid_link):
    user = User(
        username='test_user',
        hashed_password='test_password'
    )
    db_session.add(user)
    await db_session.commit()
    user_link = Link(
        owner=user.username,
        link=valid_link.link,
        code=valid_link.code,
        created_at=valid_link.created_at,
        updated_at=valid_link.updated_at,
        usage_count=valid_link.usage_count,
        expires_at=valid_link.expires_at
    )
    await add_valid_link(db_session, user_link)
    user_data = UserData(
        username=user.username,
        disabled=False
    )
    link = await get_user_link(db_session, user_data, valid_link.code)
    assert link.link == valid_link.link
    assert link.owner == user.username
    
@pytest.mark.asyncio
async def test_get_user_link_raise_exception(db_session, valid_link):
    user = User(
        username='test_user',
        hashed_password='test_password'
    )
    db_session.add(user)
    await db_session.commit()
    user_link = Link(
        owner=user.username,
        link=valid_link.link,
        code=valid_link.code,
        created_at=valid_link.created_at,
        updated_at=valid_link.updated_at,
        usage_count=valid_link.usage_count,
        expires_at=valid_link.expires_at
    )
    await add_valid_link(db_session, user_link)
    fake_user = User(
        username='fake_user',
        hashed_password='test_password_fake'
    )
    db_session.add(fake_user)
    await db_session.commit()
    fake_user_data = UserData(
        username=fake_user.username,
        disabled=False
    )
    with pytest.raises(Exception):
        await get_user_link(db_session, fake_user_data, user_link.code)
