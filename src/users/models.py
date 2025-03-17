from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import String
from sqlalchemy import func
from datetime import datetime

from src.database import Base, int_pk, str_uniq


class Link(Base):
    id: Mapped[int_pk]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    link: Mapped[str_uniq]
    short_link: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=datetime.now)
    usage_count: Mapped[int] = mapped_column(server_default=text('0'))
    
    major: Mapped["User"] = relationship("User", back_populates="shortlinks")

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"owner_id={self.owner_id!r}, "
                f"link={self.link!r}, "
                f"short_link={self.short_link!r}, "
                f"created_at={self.created_at!r}, "
                f"updated_at={self.updated_at!r}, "
                f"usage_count={self.usage_count!r})")
    
    
class User(Base):
    id: Mapped[int_pk]
    username: Mapped[str_uniq]
    hashed_password: Mapped[str_uniq]

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"username={self.username!r}, "
                f"hashed_password={self.hashed_password!r})")
