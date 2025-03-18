from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, text

from src.database import Base, int_pk, str_uniq


class User(Base):
    id: Mapped[int_pk]
    username: Mapped[str_uniq]
    hashed_password: Mapped[str_uniq]
    disabled: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"username={self.username!r}, "
                f"hashed_password={self.hashed_password!r})")
