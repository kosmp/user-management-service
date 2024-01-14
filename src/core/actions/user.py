from datetime import timedelta
from typing import List

from fastapi import HTTPException, status, Depends
from pydantic import UUID4, EmailStr

from src.adapters.database.redis_connection import redis_client
from src.core import settings, oauth2_scheme
from src.ports.enums import Role
from src.adapters.database.database_settings import get_async_session
from src.core.actions.group import get_db_group, create_db_group
from src.core.services.hasher import PasswordHasher
from src.core.services.token import get_token_payload
from src.core.services.user import (
    authenticate_user,
)
from src.ports.schemas.user import (
    UserResponseModel,
    UserUpdateModel,
    CredentialsModel,
    SignUpModel,
    UserCreateModel,
    TokenData,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.core.services.token import generate_tokens


async def create_user(
    user_data: SignUpModel, db_session: AsyncSession
) -> UserResponseModel:
    group_id: UUID4 or None = None
    if user_data.group_id is not None:
        group = await get_db_group(user_data.group_id, db_session=db_session)
        if group is not None:
            group_id = group.id

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
                exclude={"password", "group_id", "role"},
                exclude_none=True,
                exclude_unset=True,
            ),
            password=hashed_password,
            group_id=group_id,
            role=user_data.role,
        )
    )

    return new_user


async def login_user(
    credentials: CredentialsModel, db_session: AsyncSession = Depends(get_async_session)
) -> dict:
    if not credentials.email or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    user = await authenticate_user(credentials, db_session=db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return generate_tokens(
        TokenData(
            user_id=str(user.id),
            role=user.role,
            group_id_user_belongs_to=str(user.group_id),
        )
    )


async def get_updated_db_user(
    user_id: UUID4, update_data: UserUpdateModel, db_session: AsyncSession
) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).update_user(user_id, update_data)


async def get_db_user_by_id(
    user_id: UUID4, db_session: AsyncSession
) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).get_user(id=user_id)


async def get_db_user_by_email(
    email: EmailStr, db_session: AsyncSession
) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).get_user(email=email)


async def delete_db_user(user_id: UUID4, db_session: AsyncSession) -> UUID4:
    return await SQLAlchemyUserRepository(db_session).delete_user(user_id)


async def get_refresh_token(refresh_token, db_session: AsyncSession) -> dict:
    if redis_client.get(str(refresh_token)) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token. Blacklisted.",
        )

    token_payload = get_token_payload(refresh_token)

    # check if user with user_id exists
    await get_db_user_by_id(user_id=token_payload.user_id, db_session=db_session)

    res = generate_tokens(**token_payload.model_dump())

    expire_time = timedelta(minutes=settings.refresh_token_expire_minutes)

    redis_client.setex(str(refresh_token), expire_time, value=1)

    return res


async def get_users_for_admin_and_moderator(
    page: int,
    limit: int,
    filter_by_name: str,
    sort_by: str,
    order_by: str,
    db_session: AsyncSession,
    token: str,
) -> List[UserResponseModel]:
    current_user_role = get_token_payload(token).role
    group_id_current_user_belongs_to = get_token_payload(token).group_id_user_belongs_to

    if current_user_role == Role.ADMIN:
        return await SQLAlchemyUserRepository(db_session).get_users(
            page=page,
            limit=limit,
            filter_by_name=filter_by_name,
            sort_by=sort_by,
            order_by=order_by,
        )
    elif current_user_role == Role.MODERATOR:
        return await SQLAlchemyUserRepository(db_session).get_users(
            page=page,
            limit=limit,
            filter_by_name=filter_by_name,
            filter_by_group_id=group_id_current_user_belongs_to,
            sort_by=sort_by,
            order_by=order_by,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with the {current_user_role} role does not have access. You are not ADMIN or MODERATOR.",
        )


async def reset_user_password(credentials: CredentialsModel):
    PasswordHasher.verify_password(
        credentials.password,
    )
