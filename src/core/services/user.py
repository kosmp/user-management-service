from fastapi.security import HTTPAuthorizationCredentials

from src.core import security
from src.adapters.database.database_settings import get_async_session
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.core.exceptions import CredentialsException
from src.core.services.token import get_token_payload
from src.ports.schemas.user import (
    CredentialsModel,
    UserResponseModel,
    UserResponseModelWithPassword,
)
from src.core.services.hasher import PasswordHasher

from fastapi import Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession


async def authenticate_user(
    credentials: CredentialsModel,
    db_session: AsyncSession,
) -> UserResponseModelWithPassword:
    login_types = ["username", "email", "phone_number"]

    user = None
    for method in login_types:
        user = await SQLAlchemyUserRepository(db_session).get_user(
            **{method: credentials.login}
        )
        if user:
            break
        else:
            continue

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are blocked."
        )

    if not PasswordHasher.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
        )

    return user


async def get_current_user_from_token(
    token: HTTPAuthorizationCredentials = Security(security),
    db_session: AsyncSession = Depends(get_async_session),
) -> UserResponseModel:
    user_id = get_token_payload(token.credentials).user_id
    user = await SQLAlchemyUserRepository(db_session).get_user(user_id=user_id)

    if user is None:
        raise CredentialsException()

    return user
