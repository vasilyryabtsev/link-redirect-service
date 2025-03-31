import pytest

from datetime import datetime

from src.archive.models import ArchivedLink


@pytest.fixture()
def valid_archivedlink():
    link = ArchivedLink(
        owner="user",
        link="http://example.com/",
        code="example_code",
        created_at=datetime.now(),
        deleted_at=datetime.now(),
        usage_count=0
    )
    return link

def test_archivedlink_repr(valid_archivedlink):
    assert valid_archivedlink.__repr__() == (
        f"ArchivedLink(id={valid_archivedlink.id!r}, "
        f"owner={valid_archivedlink.owner!r}, "
        f"link={valid_archivedlink.link!r}, "
        f"code={valid_archivedlink.code!r}, "
        f"created_at={valid_archivedlink.created_at!r}, "
        f"deleted_at={valid_archivedlink.deleted_at!r}, "
        f"usage_count={valid_archivedlink.usage_count!r})"
    )
