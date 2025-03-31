import pytest

from src.users.models import User
from src.users.service import get_password_hash


@pytest.fixture()
def valid_user():
    user = User(
        username="user",
        hashed_password=get_password_hash("password"),
        disabled=False
    )
    return user

def test_user_repr(valid_user):
    assert valid_user.__repr__() == (
        f"User(id={valid_user.id!r}, "
        f"username={valid_user.username!r}, "
        f"hashed_password={valid_user.hashed_password!r})"
    )
