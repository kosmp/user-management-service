from src.core.services.pika_client import PikaClient
from src.core.config import PydanticSettings
from fastapi.security import HTTPBearer
from pathlib import Path

settings = PydanticSettings(
    _env_file=str(Path(__file__).parent.parent.parent / ".env"),
    _env_file_encoding="utf-8",
)

security = HTTPBearer()

pika_client_instance = PikaClient(
    rabbitmq_host=settings.rabbitmq_host,
    rabbitmq_port=settings.rabbitmq_port,
    rabbitmq_vhost=settings.rabbitmq_vhost,
    rabbitmq_default_user=settings.rabbitmq_default_user,
    rabbitmq_default_pass=settings.rabbitmq_default_pass,
)
