from src.adapters.api.routes import auth, healthcheck, user, group
from src.app import app

app.include_router(healthcheck.router, tags=["Healthcheck"])
app.include_router(user.router, tags=["User"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(group.router, tags=["Group"])
