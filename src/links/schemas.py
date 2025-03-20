from datetime import datetime
from pydantic import BaseModel

class LinkData(BaseModel):
    owner: str | None = None
    link: str
    code: str
    created_at: datetime
    updated_at: datetime
    usage_count: int
    
class NewLink(BaseModel):
    link: str