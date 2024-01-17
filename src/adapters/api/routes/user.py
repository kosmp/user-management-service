from fastapi import APIRouter, Depends, Query, Security
from typing import List

from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import security
from src.core.services.token import get_token_payload
from src.core.services.user import (
    get_current_user_from_token,
    check_current_user_for_admin,
    check_current_user_for_moderator_and_admin,
)
from src.ports.schemas.user import UserResponseModel, UserUpdateModel, UserUpdateMeModel
from src.adapters.database.database_settings import get_async_session
from src.core.actions.user import (
    get_updated_db_user,
    get_db_user_by_id,
    delete_db_user,
    get_users_for_admin_and_moderator,
)

router = APIRouter()


@router.get("/users", response_model=List[UserResponseModel])
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    filter_by_name: str = None,
    sort_by: str = None,
    order_by: str = Query("asc", regex="^(asc|desc)$"),
    token: HTTPAuthorizationCredentials = Security(security),
    db_session: AsyncSession = Depends(get_async_session),
):
    return await get_users_for_admin_and_moderator(
        page, limit, filter_by_name, sort_by, order_by, db_session, token.credentials
    )


@router.get("/user/me", response_model=UserResponseModel)
async def get_me(
    current_user: UserResponseModel = Depends(get_current_user_from_token),
):
    return current_user


@router.patch("/user/me", response_model=UserResponseModel)
async def update_me(
    update_data: UserUpdateMeModel,
    token: HTTPAuthorizationCredentials = Security(security),
    db_session: AsyncSession = Depends(get_async_session),
):
    user_id = get_token_payload(token.credentials).user_id

    return await get_updated_db_user(
        user_id,
        UserUpdateModel.model_validate(update_data.model_dump()),
        db_session,
    )


@router.delete("/user/me", response_model=UUID4)
async def delete_me(
    token: HTTPAuthorizationCredentials = Security(security),
    db_session: AsyncSession = Depends(get_async_session),
):
    user_id = get_token_payload(token.credentials).user_id

    return await delete_db_user(user_id, db_session)


@router.get(
    "/user/{user_id}",
    response_model=UserResponseModel,
)
async def get_user(
    user_id: UUID4,
    token: HTTPAuthorizationCredentials = Security(security),
    db_session: AsyncSession = Depends(get_async_session),
):
    user = await get_db_user_by_id(user_id, db_session)
    await check_current_user_for_moderator_and_admin(user.group_id, token.credentials)

    return user


@router.patch(
    "/user/{user_id}/update",
    response_model=UserResponseModel,
    dependencies=[Depends(check_current_user_for_admin)],
)
async def update_user(
    user_id: UUID4,
    update_data: UserUpdateModel,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await get_updated_db_user(user_id, update_data, db_session)
