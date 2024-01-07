from datetime import timedelta, datetime
from uuid import UUID

from jose import JWTError, jwt

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

        token_data = TokenData(user_id=user_id)
        return token_data
    except JWTError:
        raise CredentialsException


def generate_token(data: TokenData, expires_delta: timedelta or None) -> str:
    to_encode = data.model_dump()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
