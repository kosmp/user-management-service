import json
from datetime import timedelta, datetime
from uuid import UUID

from jose import JWTError, jwt

from adapters.database.redis_connection import redis_client
from src.ports.schemas.user import TokenData
from src.core.exceptions import CredentialsException
from src.core import settings


def get_token_payload(token) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: UUID = payload.get("user_id")
        if user_id is None:
            raise CredentialsException

        token_data = TokenData(user_id=str(user_id))
        return token_data
    except JWTError:
        raise CredentialsException


def generate_token(payload: TokenData, expires_delta: timedelta) -> str:
    to_encode = payload.model_dump()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def generate_tokens(payload: dict) -> dict:
    payload["user_id"] = str(payload.get("user_id"))
    access_token = generate_token(
        payload=TokenData(**payload),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    refresh_token_expires = timedelta(minutes=settings.refresh_token_expire_minutes)

    refresh_token = generate_token(
        payload=TokenData(**payload),
        expires_delta=refresh_token_expires,
    )

    redis_client.setex(json.dumps(payload), refresh_token_expires, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
