from typing import Optional
from pydantic import BaseModel, HttpUrl, field_serializer
from datetime import datetime


class Url(BaseModel):
    """
    Базовая модель для представления URL.

    Attributes:
        link: Валидированный HTTP URL. Автоматически преобразуется в объект HttpUrl.
    """
    link: HttpUrl
    
    @field_serializer('link')
    def serealize_link(self, link: HttpUrl):
        """
        Сериализатор для преобразования HttpUrl в строку.

        Args:
            link: Объект HttpUrl для сериализации.

        Returns:
            Строковое представление URL.
        """
        return str(link)


class CustomUrl(Url):
    """
    Расширенная модель URL с дополнительными параметрами.

    Наследует все атрибуты от Url и добавляет:
        - срок действия ссылки
        - возможность кастомного алиаса

    Attributes:
        expires_at: Дата и время истечения срока действия ссылки.
        custom_alias: Пользовательский псевдоним для ссылки (опционально).
    """
    expires_at: datetime
    custom_alias: Optional[str] = None
    
    
class LinkData(BaseModel):
    """
    Модель для представления данных о ссылке.

    Используется для возврата статистики и метаданных о ссылке.

    Attributes:
        link: Оригинальный URL в строковом формате.
        code: Уникальный код сокращенной ссылки.
        created_at: Дата и время создания записи.
        usage_count: Количество переходов по ссылке.
        updated_at: Дата и время последнего обновления.
    """
    link: str
    code: str
    created_at: datetime
    usage_count: int
    updated_at: datetime
