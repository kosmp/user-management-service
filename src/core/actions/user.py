from datetime import timedelta
from typing import List

from fastapi import HTTPException, status
from pydantic import UUID4, EmailStr

from src.core.services.pass_reset_producer import send_message
from src.adapters.database.redis_connection import redis_client
from src.core import settings
from src.ports.enums import Role
from src.core.actions.group import get_db_group, create_db_group
from src.core.services.hasher import PasswordHasher
from src.core.services.token import get_token_payload
from src.core.services.user import (
    authenticate_user,
)
from src.ports.schemas.user import (
    UserResponseModel,
    UserUpdateModel,
    CredentialsEmailModel,
    SignUpModel,
    UserCreateModel,
    TokenData,
    PasswordModel,
    CredentialsUsernameModel,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.core.services.token import generate_tokens


async def create_user(
    user_data: SignUpModel, db_session: AsyncSession
) -> UserResponseModel:
    group_id = None
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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Group name is required."
        )

    hashed_password = PasswordHasher.get_password_hash(user_data.password)

    user_data_dict = user_data.model_dump(
        exclude={"password", "group_id"},
        include={"password": hashed_password, "group_id": group_id},
        exclude_none=True,
        exclude_unset=True,
    )
    new_user = await SQLAlchemyUserRepository(db_session).create_user(
        UserCreateModel.model_validate(user_data_dict)
    )

    return new_user


async def login_user(
    credentials: CredentialsEmailModel | CredentialsUsernameModel,
    db_session: AsyncSession,
) -> dict:
    if isinstance(credentials, CredentialsEmailModel):
        if not credentials.email or not credentials.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )
    elif isinstance(credentials, CredentialsUsernameModel):
        if not credentials.username or not credentials.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password",
            )

    user = await authenticate_user(credentials, db_session=db_session)

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
    return await SQLAlchemyUserRepository(db_session).get_user(user_id=user_id)


async def get_db_user_by_email(
    email: EmailStr, db_session: AsyncSession
) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).get_user(email=email)


async def get_db_user_by_username(
    username: str, db_session: AsyncSession
) -> UserResponseModel:
    return await SQLAlchemyUserRepository(db_session).get_user(username=username)


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
    payload = get_token_payload(token)

    if payload.role == Role.ADMIN:
        return await SQLAlchemyUserRepository(db_session).get_users(
            page=page,
            limit=limit,
            filter_by_name=filter_by_name,
            sort_by=sort_by,
            order_by=order_by,
        )
    elif payload.role == Role.MODERATOR:
        return await SQLAlchemyUserRepository(db_session).get_users(
            page=page,
            limit=limit,
            filter_by_name=filter_by_name,
            filter_by_group_id=payload.group_id_user_belongs_to,
            sort_by=sort_by,
            order_by=order_by,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with the {payload.role} role does not have access. You are not ADMIN or MODERATOR.",
        )


async def request_reset_user_password(email: EmailStr, db_session):
    user = await get_db_user_by_email(email, db_session)

    tokens = generate_tokens(
        TokenData(
            user_id=str(user.id),
            role=user.role,
            group_id_user_belongs_to=str(user.group_id),
        )
    )
    access_token = tokens["access_token"]

    reset_link = f"${settings.web_url}/reset-password?token={access_token}"

    send_message(str(email), reset_link)

    return {"success": True}


async def reset_user_password(
    token: str, new_password: PasswordModel, db_session: AsyncSession
):
    payload = get_token_payload(token)
    user_id = payload.get("user_id")

    hashed_password = PasswordHasher.get_password_hash(str(new_password))

    return await SQLAlchemyUserRepository(db_session).update_password(
        user_id, hashed_password
    )
