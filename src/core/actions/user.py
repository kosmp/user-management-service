from datetime import timedelta

from fastapi import HTTPException, status, Depends
from pydantic import UUID5, EmailStr

from adapters.database.database_settings import get_async_session
from core import settings
from core.actions.group import get_db_group, create_db_group
from core.services.hasher import PasswordHasher
from core.services.token import generate_token
from core.services.user import authenticate_user
from src.ports.schemas.user import (
    UserResponseModel,
    UserUpdateModel,
    CredentialsModel,
    TokenData,
    SignUpModel,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.ports.schemas.user import UserCreateModel


async def create_user(
    user_data: SignUpModel, db_session: AsyncSession
) -> UserResponseModel:
    user_exists = get_db_user_by_email(user_data.email, db_session=db_session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already exists"
        )

    group_id = None
    if user_data.group_id is not None:
        group_id = (await get_db_group(user_data.group_id, db_session=db_session)).id

    if group_id is None and user_data.group_name is not None:
        group_id = (
            await create_db_group(user_data.group_name, db_session=db_session)
        ).id
    elif group_id is None and user_data.group_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Group name is required"
        )

    hashed_password = PasswordHasher.get_password_hash(user_data.password)

    new_user = await SQLAlchemyUserRepository(db_session).create_user(
        UserCreateModel(
            **user_data.model_dump(
                exclude={"password", "group_id"},
                include={"password": hashed_password, "group_id": group_id},
            )
        )
    )

    return new_user


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


async def get_updated_db_user(
    user_id: UUID5, update_data: UserUpdateModel, db_session: AsyncSession
) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).update_user(
        user_id, **update_data.model_dump()
    )


async def get_db_user_by_id(
    user_id: UUID5, db_session: AsyncSession
) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).get_user(id=user_id)


async def get_db_user_by_email(
    email: EmailStr, db_session: AsyncSession
) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).get_user(email=email)


async def block_db_user(user_id: UUID5, db_session: AsyncSession) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).block_user(user_id)


async def delete_db_user(user_id: UUID5, db_session: AsyncSession) -> UUID5:
    return await SQLAlchemyUserRepository(db_session).delete_user(user_id)
