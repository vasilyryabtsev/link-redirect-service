from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import String, DateTime
from sqlalchemy import func
from datetime import datetime

from src.database import Base, int_pk, str_uniq
from src.users.models import User


class Link(Base):
    id: Mapped[int_pk]
    owner: Mapped[int] = mapped_column(ForeignKey("users.username"), nullable=True)
    link: Mapped[str_uniq]
    code: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_count: Mapped[int] = mapped_column(server_default=text('0'))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user: Mapped["User"] = relationship("User", back_populates="links")

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"owner={self.owner!r}, "
                f"link={self.link!r}, "
                f"code={self.code!r}, "
                f"created_at={self.created_at!r}, "
                f"updated_at={self.updated_at!r}, "
                f"usage_count={self.usage_count!r}, "
                f"expires_at={self.expires_at!r})")

