from datetime import datetime

from archive.models import ArchivedLink

def test_archivedlink_repr():
    link = ArchivedLink(
        id=1,
        owner="user",
        link="http://example.com/",
        code="Zdjflks32",
        created_at='2025-03-29 17:52:46.794823',
        deleted_at='2025-03-29 17:52:46.794823',
        usage_count=0
    )
    assert link.__repr__() == (
        f"ArchivedLink(id=1, "
        f"owner='user', "
        f"link='http://example.com/', "
        f"code='Zdjflks32', "
        f"created_at='2025-03-29 17:52:46.794823', "
        f"deleted_at='2025-03-29 17:52:46.794823', "
        f"usage_count=0)"
    )
