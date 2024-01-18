import pika
from pika.adapters.blocking_connection import BlockingConnection
from pika.credentials import PlainCredentials
from src.core.config import PydanticSettings
from fastapi.security import HTTPBearer
from pathlib import Path

settings = PydanticSettings(
    _env_file=str(Path(__file__).parent.parent.parent / ".env"),
    _env_file_encoding="utf-8",
)

security = HTTPBearer()


def open_rabbit_connection() -> BlockingConnection:
    credentials = PlainCredentials(
        settings.rabbitmq_default_user, settings.rabbitmq_default_pass
    )

    connection_parameters = pika.ConnectionParameters(
        "app-rabbitmq", settings.rabbitmq_port, "/", credentials
    )

    conn = pika.BlockingConnection(connection_parameters)

    return conn


rabbit_connection = open_rabbit_connection()


def close_rabbit_connection(conn: BlockingConnection):
    conn.close()
