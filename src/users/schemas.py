from pydantic import BaseModel


class RegUser(BaseModel):
    username: str
    password: str
    
# User
class UserData(BaseModel):
    username: str | None = None
    disabled: bool | None = None
    
class Message(BaseModel):
    text: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserInDB(UserData):
    hashed_password: str
