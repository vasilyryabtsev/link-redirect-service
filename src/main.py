import uvicorn
from fastapi import FastAPI

from src.users.auth import router as auth_rounter

app = FastAPI()
app.include_router(auth_rounter)
