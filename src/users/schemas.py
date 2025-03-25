from pydantic import BaseModel


class RegUser(BaseModel):
    username: str
    password: str
    
class UserData(BaseModel):
    username: str | None = None
    disabled: bool | None = None
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
