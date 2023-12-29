from fastapi import APIRouter

from src.adapters.api.routes import auth, healthcheck, user, group
from src.app import app

main_router = APIRouter()

app.include_router(healthcheck.router, tags=["Healthcheck"])

main_router.include_router(user.router, tags=["User v1"])
main_router.include_router(auth.router, tags=["Auth v1"])
main_router.include_router(group.router, tags=["Group v1"])

app.include_router(main_router, prefix="v1")
