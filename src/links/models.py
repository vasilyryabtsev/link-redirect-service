from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import String, DateTime, Integer
from datetime import datetime

from src.database import Base, int_pk, str_uniq
from src.users.models import User


class Link(Base):
    """
    Модель для хранения информации о сокращенных ссылках.

    Содержит данные о ссылке, включая владельца, оригинальный URL, сокращенный код,
    даты создания, обновления и истечения срока действия, а также счетчик переходов.

    Attributes:
        id: Уникальный идентификатор ссылки (первичный ключ).
        owner: Имя пользователя-владельца ссылки (внешний ключ). Может быть None.
        link: Оригинальный URL (уникальный).
        code: Сокращенный код ссылки. Может быть None.
        created_at: Дата и время создания записи. Может быть None.
        updated_at: Дата и время последнего обновления. Может быть None.
        usage_count: Количество переходов по ссылке (по умолчанию 0).
        expires_at: Дата и время истечения срока действия ссылки. Может быть None.
        user: Связь с моделью пользователя (relationship).
    """

    id: Mapped[int_pk]
    owner: Mapped[str] = mapped_column(String, ForeignKey("users.username"), nullable=True)
    link: Mapped[str_uniq]
    code: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user: Mapped["User"] = relationship("User", back_populates="links")

    def __repr__(self):
        """Генерирует строковое представление объекта Link для отладки.

        Returns:
            Строка, содержащая все основные атрибуты объекта.
        """
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"owner={self.owner!r}, "
                f"link={self.link!r}, "
                f"code={self.code!r}, "
                f"created_at={self.created_at!r}, "
                f"updated_at={self.updated_at!r}, "
                f"usage_count={self.usage_count!r}, "
                f"expires_at={self.expires_at!r})")
