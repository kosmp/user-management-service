from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.ports.schemas.user import UserResponseModel, UserUpdateModel
from src.adapters.database.database_settings import get_async_session
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.core.services.token import get_token_data
from src.core.actions.user import get_updated_db_user, get_db_user, block_db_user

router = APIRouter()

# here only for development
SECRET_KEY = "test_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
async def get_me(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
):
    token_data = get_token_data(token)

    return await get_db_user(token_data.user_id, db_session)


@router.patch("/user/me", response_model=UserResponseModel)
async def update_me(
    update_data: UserUpdateModel,
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
):
    user_id = get_token_data(token).user_id

    return await get_updated_db_user(user_id, update_data, db_session)


@router.delete("/user/me", response_model=UserResponseModel)
async def delete_me(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
):
    user_id = get_token_data(token).user_id

    deleted_user_id = await SQLAlchemyUserRepository(db_session).delete_user(user_id)

    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail="User not found for deletion")

    return deleted_user_id


@router.get("/user/{user_id}", response_model=UserResponseModel)
async def get_user(user_id: str, db_session: AsyncSession = Depends(get_async_session)):
    return await get_db_user(user_id, db_session)


@router.patch("/user/{user_id}/update", response_model=UserResponseModel)
async def update_user(
    user_id: str,
    update_data: UserUpdateModel,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await get_updated_db_user(user_id, update_data, db_session)


@router.patch("/user/{user_id}/block", response_model=UserResponseModel)
async def block_user(
    user_id: str,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await block_db_user(user_id, db_session)
