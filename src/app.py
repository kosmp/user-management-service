from fastapi import FastAPI
from py_fastapi_logging.middlewares.logging import LoggingMiddleware

app = FastAPI()

app.add_middleware(LoggingMiddleware, app_name="user-management-service")
