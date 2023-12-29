from fastapi import APIRouter

from src.adapters.api.routes import auth, healthcheck, user, group
from src.app import app

app.include_router(healthcheck.router, tags=["Healthcheck"])

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(user.router)
v1_router.include_router(auth.router)
v1_router.include_router(group.router)

app.include_router(v1_router)
