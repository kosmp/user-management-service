from fastapi import FastAPI
from py_fastapi_logging.middlewares.logging import LoggingMiddleware
from src.core import rabbit_connection, close_rabbit_connection

app = FastAPI()

app.add_middleware(LoggingMiddleware, app_name="user-management-service")


@app.on_event("shutdown")
def shutdown_event():
    close_rabbit_connection(rabbit_connection)
