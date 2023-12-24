from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import UUID

from src.ports.schemas.user import UserResponseModel, UserUpdateModel
from src.adapters.database.database_settings import get_async_session
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

router = APIRouter()


@router.get("/users", response_model=List[UserResponseModel])
async def get_users(
    page: int = 1,
    limit: int = 30,
    filter_by_name: str = None,
    sort_by: str = None,
    order_by: str = "asc",
    db_session: AsyncSession = Depends(get_async_session),
):
    db_users = await SQLAlchemyUserRepository(db_session).get_users(
        page, limit, filter_by_name, sort_by, order_by
    )
    if len(db_users) == 0:
        raise HTTPException(status_code=404, detail="Users not found")
    return db_users


@router.get("/user/me", response_model=UserResponseModel)
async def get_me(db_session: AsyncSession = Depends(get_async_session)):
    pass


@router.patch("/user/me", response_model=UserResponseModel)
async def update_me(
    update_data: UserUpdateModel, db_session: AsyncSession = Depends(get_async_session)
):
    pass


@router.delete("/user/me", response_model=UserResponseModel)
async def delete_me(db_session: AsyncSession = Depends(get_async_session)):
    pass


@router.get("/user/{user_id}", response_model=UserResponseModel)
async def get_user(
    user_id: UUID, db_session: AsyncSession = Depends(get_async_session)
):
    db_user = await SQLAlchemyUserRepository(db_session).get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/user/{user_id}", response_model=UserResponseModel)
async def update_user(
    user_id: UUID,
    update_data: UserUpdateModel,
    db_session: AsyncSession = Depends(get_async_session),
):
    result_user = await SQLAlchemyUserRepository(db_session).update_user(
        user_id, **update_data.model_dump()
    )
    if result_user is None:
        raise HTTPException(
            status_code=404, detail="User not found. So can't be updated"
        )
    return result_user
