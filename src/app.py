from fastapi import FastAPI
from py_fastapi_logging.middlewares.logging import LoggingMiddleware
from src.core import settings

app = FastAPI()

if not settings.test_mode:
    app.add_middleware(LoggingMiddleware, app_name="user-management-service")
