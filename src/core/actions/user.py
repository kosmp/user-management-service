from fastapi import HTTPException
from pydantic import UUID5

from src.ports.schemas.user import UserResponseModel, UserUpdateModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


async def get_updated_db_user(
    user_id: UUID5, update_data: UserUpdateModel, db_session: AsyncSession
) -> UserResponseModel:
    result_user = await SQLAlchemyUserRepository(db_session).update_user(
        user_id, **update_data.model_dump()
    )

    if result_user is None:
        raise HTTPException(
            status_code=404, detail="User not found. So can't be updated"
        )
    return result_user


async def get_db_user(user_id: UUID5, db_session: AsyncSession) -> UserResponseModel:
    db_user = await SQLAlchemyUserRepository(db_session).get_user(user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


async def block_db_user(user_id: UUID5, db_session: AsyncSession) -> UserResponseModel:
    result_user = await SQLAlchemyUserRepository(db_session).block_user(user_id)

    if result_user is None:
        raise HTTPException(
            status_code=404, detail="User not found. So can't be blocked"
        )
    return result_user


async def delete_db_user(user_id: UUID5, db_session: AsyncSession) -> UUID5:
    deleted_user_id = await SQLAlchemyUserRepository(db_session).delete_user(user_id)

    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail="User not found for deletion")

    return deleted_user_id
