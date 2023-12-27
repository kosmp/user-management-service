from uuid import UUID

from jose import JWTError, jwt
from fastapi import HTTPException, status
from src.ports.schemas.user import TokenData


def get_token_data(token) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: UUID = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id)
        return token_data
    except JWTError:
        raise credentials_exception
