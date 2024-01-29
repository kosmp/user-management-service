from datetime import timedelta, datetime

from jose import JWTError, jwt

from src.logging_config import logger
from src.ports.enums import TokenType
from src.ports.schemas.user import TokenData, TokensResult, TokenDataWithTokenType
from src.core.exceptions import CredentialsException
from src.core import settings


def get_token_payload(token: str) -> TokenDataWithTokenType:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        token_data = TokenDataWithTokenType(**payload)
        return token_data
    except JWTError:
        logger.error("Invalid token. Can not be decoded.")
        raise CredentialsException("Invalid token.")


def generate_token(payload: TokenDataWithTokenType, expires_delta: timedelta) -> str:
    to_encode = payload.model_dump()
    to_encode.update({"exp": datetime.now() + expires_delta})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def generate_tokens(payload: TokenData) -> TokensResult:
    access_token_payload = payload.model_dump()
    access_token_payload.update({"token_type": TokenType.ACCESS})
    access_token = generate_token(
        payload=TokenDataWithTokenType.model_validate(access_token_payload),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    refresh_token_expires = timedelta(minutes=settings.refresh_token_expire_minutes)

    refresh_token_payload = payload.model_dump()
    refresh_token_payload.update({"token_type": TokenType.REFRESH})
    refresh_token = generate_token(
        payload=TokenDataWithTokenType.model_validate(refresh_token_payload),
        expires_delta=refresh_token_expires,
    )

    return TokensResult(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )
