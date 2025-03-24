import redis

from fastapi import FastAPI
from src.users.auth import router as auth_router
from src.users.router import router as user_router
from src.links.router import router as link_router


app = FastAPI()
redis_client = redis.Redis(host='reddis_app', port=6379, db=0)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(link_router)
