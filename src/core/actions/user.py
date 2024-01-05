from pydantic import UUID5, EmailStr

from src.ports.schemas.user import UserResponseModel, UserUpdateModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


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
