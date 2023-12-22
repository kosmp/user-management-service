from src.adapters.api.routes import auth, healthcheck, user
from src.app import app

app.include_router(healthcheck.router, tags=["Healthcheck"])
app.include_router(user.router, tags=["User"])
app.include_router(auth.router, tags=["Auth"])
