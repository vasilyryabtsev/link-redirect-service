import pytest

from datetime import datetime

from src.links.models import Link


@pytest.fixture()
def valid_link():
    link = Link(
        owner=None,
        link="http://example.com/",
        code="example_code",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        usage_count=0,
        expires_at=datetime.now()
    )
    return link

def test_link_repr(valid_link):
    assert valid_link.__repr__() == (
        f"Link(id={valid_link.id!r}, "
        f"owner={valid_link.owner!r}, "
        f"link={valid_link.link!r}, "
        f"code={valid_link.code!r}, "
        f"created_at={valid_link.created_at!r}, "
        f"updated_at={valid_link.updated_at!r}, "
        f"usage_count={valid_link.usage_count!r}, "
        f"expires_at={valid_link.expires_at!r})"
    )
