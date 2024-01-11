from typing import Union

from src.adapters.database.database_settings import get_async_session
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.core import oauth2_scheme
from src.core.exceptions import CredentialsException
from src.core.services.token import get_token_payload
from src.ports.schemas.user import (
    CredentialsModel,
    UserResponseModel,
    UserResponseModelWithPassword,
)
from src.core.services.hasher import PasswordHasher

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def authenticate_user(
    credentials: CredentialsModel, db_session: AsyncSession
) -> Union[UserResponseModelWithPassword, None]:
    user = await SQLAlchemyUserRepository(db_session).get_user(email=credentials.email)
    if user is None:
        return
    if not PasswordHasher.verify_password(credentials.password, user.password):
        return
    return user


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
) -> UserResponseModel:
    user_id = get_token_payload(token).user_id
    user = await SQLAlchemyUserRepository(db_session).get_user(id=user_id)

    if user is None:
        raise CredentialsException

    return user
