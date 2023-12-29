from uuid import UUID

from jose import JWTError, jwt
from src.ports.schemas.user import TokenData
from src.core.exceptions import CredentialsException
from src.core import settings


def get_token_data(token) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: UUID = payload.get("sub")
        if user_id is None:
            raise CredentialsException

        token_data = TokenData(user_id=user_id)
        return token_data
    except JWTError:
        raise CredentialsException
