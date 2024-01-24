from datetime import timedelta
from typing import List, Union

from fastapi import HTTPException, status, UploadFile
from pydantic import UUID4, EmailStr

from src.core.exceptions import CredentialsException
from src.adapters.database.repositories.sqlalchemy_group_repository import (
    SQLAlchemyGroupRepository,
)
from src.core.services.pika_client import pika_client_instance
from src.adapters.database.redis_connection import redis_client
from src.core import settings
from src.ports.enums import Role, TokenType
from src.core.actions.group import get_db_group, create_db_group
from src.core.services.hasher import PasswordHasher
from src.core.services.token import get_token_payload
from src.core.services.user import (
    authenticate_user,
)
from src.ports.schemas.user import (
    UserResponseModel,
    UserUpdateModelWithoutImage,
    UserUpdateModelWithImage,
    CredentialsModel,
    SignUpModel,
    UserCreateModel,
    TokenData,
    PasswordModel,
    TokensResult,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.core.services.token import generate_tokens
from src.core.services.file_service import upload_image, delete_old_image, validate_file


async def create_user(
    user_data: SignUpModel,
    db_session: AsyncSession,
    image_file: Union[UploadFile, None] = None,
) -> UserResponseModel:
    group_id = None
    if user_data.group_id is not None:
        group = await get_db_group(user_data.group_id, db_session=db_session)
        if group is not None:
            group_id = group.id

    if group_id is None and user_data.group_name is not None:
        group_id = (
            await SQLAlchemyGroupRepository(db_session).create_group(
                user_data.group_name
            )
        ).id
    elif group_id is None and user_data.group_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Group name is required."
        )

    hashed_password = PasswordHasher.get_password_hash(user_data.password)

    await validate_file(image_file)
    user_data_dict = user_data.__dict__
    user_data_dict.update(
        {
            "password": hashed_password,
            "group_id": group_id,
            "image": await upload_image(image_file, user_data.username)
            if image_file
            else None,
        }
    )

    new_user = await SQLAlchemyUserRepository(db_session).create_user(
        UserCreateModel.model_validate(user_data_dict)
    )

    await db_session.commit()

    return new_user


async def login_user(
    credentials: CredentialsModel,
    db_session: AsyncSession,
) -> TokensResult:
    if not credentials.login or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect login or password",
        )

    user = await authenticate_user(credentials, db_session=db_session)

    return generate_tokens(
        TokenData(
            user_id=str(user.id),
            role=user.role,
            group_id=str(user.group_id),
            is_blocked=user.is_blocked,
        )
    )


async def get_updated_db_user(
    user_id: UUID4,
    update_data: UserUpdateModelWithoutImage,
    db_session: AsyncSession,
    image_file: Union[UploadFile, None] = None,
) -> UserResponseModel:
    user = await SQLAlchemyUserRepository(db_session).get_user(user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if update_data.group_id is not None:
        await get_db_group(update_data.group_id, db_session)

    image_url = None
    if image_file is not None:
        if user.image is not None and await validate_file(image_file):
            await delete_old_image(user.image)
        image_url = await upload_image(image_file, str(user_id))

    update_model = update_data.model_dump()
    update_model.update({"image": image_url})
    user_data_dict = UserUpdateModelWithImage.model_validate(update_model)

    return await SQLAlchemyUserRepository(db_session).update_user(
        user_id, user_data_dict
    )


async def get_db_user_by_id(
    user_id: UUID4, db_session: AsyncSession
) -> UserResponseModel:
    user = await SQLAlchemyUserRepository(db_session).get_user(user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


async def get_db_user_by_email(
    email: EmailStr, db_session: AsyncSession
) -> UserResponseModel:
    user = await SQLAlchemyUserRepository(db_session).get_user(email=str(email))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


async def get_db_user_by_username(
    username: str, db_session: AsyncSession
) -> UserResponseModel:
    user = await SQLAlchemyUserRepository(db_session).get_user(username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


async def delete_db_user(user_id: UUID4, db_session: AsyncSession) -> UUID4:
    return await SQLAlchemyUserRepository(db_session).delete_user(user_id)


async def refresh_tokens(refresh_token, db_session: AsyncSession) -> TokensResult:
    if redis_client.get(str(refresh_token)) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token. Blacklisted.",
        )

    token_payload = get_token_payload(refresh_token)

    if token_payload.token_type != TokenType.REFRESH:
        raise CredentialsException("Invalid token type. It's not a refresh token.")

    # check if user with user_id exists
    await get_db_user_by_id(user_id=token_payload.user_id, db_session=db_session)

    res = generate_tokens(token_payload)

    expire_time = timedelta(minutes=settings.refresh_token_expire_minutes)

    redis_client.setex(str(refresh_token), expire_time, value=1)

    return res


async def get_users_for_admin_and_moderator(**kwargs) -> List[UserResponseModel]:
    payload = get_token_payload(kwargs.get("token"))

    if payload.role == Role.ADMIN:
        return await SQLAlchemyUserRepository(kwargs.get("db_session")).get_users(
            page=kwargs.get("page"),
            limit=kwargs.get("limit"),
            filter_by_name=kwargs.get("filter_by_name"),
            filter_by_surname=kwargs.get("filter_by_surname"),
            sort_by=kwargs.get("sort_by"),
            order_by=kwargs.get("order_by"),
        )
    elif payload.role == Role.MODERATOR:
        return await SQLAlchemyUserRepository(kwargs.get("db_session")).get_users(
            page=kwargs.get("page"),
            limit=kwargs.get("limit"),
            filter_by_name=kwargs.get("filter_by_name"),
            filter_by_surname=kwargs.get("filter_by_surname"),
            filter_by_group_id=payload.group_id,
            sort_by=kwargs.get("sort_by"),
            order_by=kwargs.get("order_by"),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with the {payload.role} role does not have access. You are not ADMIN or MODERATOR.",
        )


async def request_reset_user_password(email: EmailStr, db_session):
    user = await get_db_user_by_email(email, db_session)

    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are blocked."
        )

    tokens = generate_tokens(
        TokenData(
            user_id=str(user.id),
            role=user.role,
            group_id=str(user.group_id),
            is_blocked=user.is_blocked,
        )
    )
    access_token = tokens.access_token

    reset_link = f"{settings.http_schema}://{settings.host}:{settings.port}/reset-password?token={access_token}"

    pika_client_instance.send_message(str(email), reset_link, "reset-password-stream")

    return {"success": True}


async def reset_user_password(
    token: str, new_password: PasswordModel, db_session: AsyncSession
) -> UserResponseModel:
    payload = get_token_payload(token)
    user_id = payload.user_id

    if payload.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are blocked."
        )

    hashed_password = PasswordHasher.get_password_hash(new_password.password)

    return await SQLAlchemyUserRepository(db_session).update_password(
        user_id, hashed_password
    )
