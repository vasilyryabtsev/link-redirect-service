from typing import Annotated
from fastapi import APIRouter, Depends

from src.users.schemas import UserData
from src.users.service import get_current_active_user

router = APIRouter(prefix='/user', tags=['User'])

@router.get("/me/", response_model=UserData)
async def read_users_me(
    current_user: Annotated[UserData, Depends(get_current_active_user)],
):
    return current_user