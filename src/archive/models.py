from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, DateTime, Integer
from datetime import datetime

from src.database import Base, int_pk


class ArchivedLink(Base):
    id: Mapped[int_pk]
    owner: Mapped[str] = mapped_column(String, nullable=True)
    link: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer)
    
    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"owner={self.owner!r}, "
                f"link={self.link!r}, "
                f"code={self.code!r}, "
                f"created_at={self.created_at!r}, "
                f"deleted_at={self.deleted_at!r}, "
                f"usage_count={self.usage_count!r})")
