from datetime import datetime

from links.models import Link

def test_link_repr():
    link = Link(
        id=1,
        owner="user",
        link="http://example.com/",
        code="Zdjflks32",
        created_at='2025-03-29 17:52:46.794823',
        updated_at='2025-03-29 17:52:46.794823',
        usage_count=0,
        expires_at='2025-03-29 17:52:46.794823'
    )
    assert link.__repr__() == (
        f"Link(id=1, "
        f"owner='user', "
        f"link='http://example.com/', "
        f"code='Zdjflks32', "
        f"created_at='2025-03-29 17:52:46.794823', "
        f"updated_at='2025-03-29 17:52:46.794823', "
        f"usage_count=0, "
        f"expires_at='2025-03-29 17:52:46.794823')"
    )
