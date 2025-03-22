from typing import Optional
from pydantic import BaseModel, HttpUrl, field_serializer
from datetime import datetime

class Url(BaseModel):
    link: HttpUrl
    
    @field_serializer('link')
    def serealize_link(self, link: HttpUrl):
        return str(link)

class CustomUrl(Url):
    expires_at: datetime
    custom_alias: Optional[str] = None
    
    
class LinkData(BaseModel):
    link: str
    code: str
    created_at: datetime
    usage_count: int
    updated_at: datetime
