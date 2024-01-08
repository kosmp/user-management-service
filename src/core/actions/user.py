from fastapi import HTTPException, status, Depends
from pydantic import UUID5, EmailStr

from src.adapters.database.database_settings import get_async_session
from src.core.actions.group import get_db_group, create_db_group
from src.core.services.hasher import PasswordHasher
from src.core.services.token import get_token_payload
from src.core.services.user import authenticate_user
from src.ports.schemas.user import (
    UserResponseModel,
    UserUpdateModel,
    CredentialsModel,
    SignUpModel,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.ports.schemas.user import UserCreateModel
from src.core.services.token import generate_tokens
from src.adapters.database.redis_connection import redis_client


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

    return generate_tokens({"user_id": user.id})


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


async def get_refresh_token(refresh_token, db_session: AsyncSession) -> dict:
    token_payload = get_token_payload(refresh_token)

    # check if user with user_id exists
    await get_db_user_by_id(user_id=token_payload.user_id, db_session=db_session)

    if await redis_client.exists(token_payload.user_id):
        redis_client.delete(token_payload.user_id)

    return generate_tokens(token_payload.model_dump())
