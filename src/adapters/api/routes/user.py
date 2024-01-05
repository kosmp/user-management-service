from fastapi import APIRouter, Depends, Query
from typing import List

from pydantic import UUID5
from sqlalchemy.ext.asyncio import AsyncSession

from src.ports.schemas.user import UserResponseModel, UserUpdateModel
from src.adapters.database.database_settings import get_async_session
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.core.services.token import get_token_data
from src.core.actions.user import (
    get_updated_db_user,
    get_db_user_by_id,
    block_db_user,
    delete_db_user,
)
from src.core import oauth2_scheme

router = APIRouter()


@router.get("/users", response_model=List[UserResponseModel])
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    filter_by_name: str = None,
    sort_by: str = None,
    order_by: str = Query("asc", regex="^(asc|desc)$"),
    db_session: AsyncSession = Depends(get_async_session),
):
    return await SQLAlchemyUserRepository(db_session).get_users(
        page, limit, filter_by_name, sort_by, order_by
    )


@router.get("/user/me", response_model=UserResponseModel)
async def get_me(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
):
    token_data = get_token_data(token)

    return await get_db_user_by_id(token_data.user_id, db_session)


@router.patch("/user/me", response_model=UserResponseModel)
async def update_me(
    update_data: UserUpdateModel,
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
):
    user_id = get_token_data(token).user_id

    return await get_updated_db_user(user_id, update_data, db_session)


@router.delete("/user/me", response_model=str)
async def delete_me(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
):
    user_id = get_token_data(token).user_id

    return await delete_db_user(user_id, db_session)


@router.get("/user/{user_id}", response_model=UserResponseModel)
async def get_user(
    user_id: UUID5, db_session: AsyncSession = Depends(get_async_session)
):
    return await get_db_user_by_id(user_id, db_session)


@router.patch("/user/{user_id}/update", response_model=UserResponseModel)
async def update_user(
    user_id: UUID5,
    update_data: UserUpdateModel,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await get_updated_db_user(user_id, update_data, db_session)


@router.patch("/user/{user_id}/block", response_model=UserResponseModel)
async def block_user(
    user_id: UUID5,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await block_db_user(user_id, db_session)
