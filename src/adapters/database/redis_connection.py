import redis
from src.core import settings

redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, password=settings.redis_password
)
