from typing import Annotated
from fastapi import Depends

from src.users.service import get_current_user
from src.users.schemas import UserData
    
def get_code(link):
    return '123'