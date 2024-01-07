from datetime import timedelta
from typing import Union

from adapters.database.database_settings import get_async_session
from core import settings, oauth2_scheme
from core.exceptions import CredentialsException
from core.services.token import generate_token, get_token_payload
from src.ports.schemas.user import (
    SignUpModel,
    CredentialsModel,
    UserResponseModel,
    TokenData,
)
from src.core.services.hasher import PasswordHasher
from src.ports.schemas.user import UserCreateModel
from src.core.actions.user import (
    get_db_user_by_email,
    create_db_user,
    get_db_user_by_id,
)

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(user_data: SignUpModel, db_session: AsyncSession):
    user_exists = get_db_user_by_email(user_data.email, db_session=db_session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already exists"
        )

    hashed_password = PasswordHasher.get_password_hash(user_data.password)

    new_user = await create_db_user(
        UserCreateModel(
            **user_data.model_dump(
                exclude={"password"}, include={"password": hashed_password}
            )
        ),
        db_session,
    )

    return new_user


async def authenticate_user(
    credentials: CredentialsModel, db_session: AsyncSession
) -> Union[UserResponseModel, None]:
    user = await get_db_user_by_email(email=credentials.email, db_session=db_session)
    if user is None:
        return
    if not PasswordHasher.verify_password(credentials.password, user):
        return
    return user


async def login_user(
    credentials: CredentialsModel, db_session: AsyncSession = Depends(get_async_session)
) -> dict:
    if credentials.email and credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    user = await authenticate_user(credentials, db_session=db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = generate_token(
        data=TokenData(user_id=user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    refresh_token = generate_token(
        data=TokenData(user_id=user.id),
        expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
) -> UserResponseModel:
    user_id = get_token_payload(token).user_id
    user = await get_db_user_by_id(user_id=user_id, db_session=db_session)

    if user is None:
        raise CredentialsException

    return user
