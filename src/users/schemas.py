from pydantic import BaseModel

class RegUser(BaseModel):
    username: str
    password: str
    
class UserData(BaseModel):
    username: str | None = None
    hashed_password: str | None = None
    disabled: bool | None = None
    
class Message(BaseModel):
    text: str