from uuid import UUID

from jose import JWTError, jwt
from src.ports.schemas.user import TokenData
from src.core.exceptions import CredentialsException


def get_token_data(token) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: UUID = payload.get("sub")
        if user_id is None:
            raise CredentialsException

        token_data = TokenData(user_id=user_id)
        return token_data
    except JWTError:
        raise CredentialsException
