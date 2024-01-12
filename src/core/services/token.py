from datetime import timedelta, datetime

from jose import JWTError, jwt

from src.ports.schemas.user import TokenData
from src.core.exceptions import CredentialsException
from src.core import settings


def get_token_payload(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        payload["user_id"] = str(payload.get("user_id"))
        payload["group_id_user_belongs_to"] = str(
            payload.get("group_id_user_belongs_to")
        )
        token_data = TokenData(**payload)
        return token_data
    except JWTError:
        raise CredentialsException


def generate_token(payload: TokenData, expires_delta: timedelta) -> str:
    to_encode = payload.model_dump()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def generate_tokens(payload: TokenData) -> dict:
    payload.user_id = str(payload.user_id)
    payload.group_id_user_belongs_to = str(payload.group_id_user_belongs_to)
    access_token = generate_token(
        payload=TokenData(**payload.model_dump()),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    refresh_token_expires = timedelta(minutes=settings.refresh_token_expire_minutes)

    refresh_token = generate_token(
        payload=TokenData(**payload.model_dump()),
        expires_delta=refresh_token_expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
