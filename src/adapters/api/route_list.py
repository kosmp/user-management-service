from src.adapters.api.routes import auth, healthcheck, user, group
from src.app import app

app.include_router(healthcheck.router, tags=["Healthcheck"])
app.include_router(user.router, prefix="/v1", tags=["User v1"])
app.include_router(auth.router, prefix="/v1", tags=["Auth v1"])
app.include_router(group.router, prefix="/v1", tags=["Group v1"])
