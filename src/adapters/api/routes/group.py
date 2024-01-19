from fastapi import APIRouter, Depends
from pydantic import UUID4

from src.core.permissions import check_curr_user_for_block_status
from src.core.permissions import check_current_user_for_admin
from src.ports.schemas.group import GroupResponseModel, GroupNameType
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.database_settings import get_async_session
from src.core.actions.group import get_db_group, delete_db_group, create_db_group

router = APIRouter()


@router.post(
    "/group",
    response_model=GroupResponseModel,
    dependencies=[
        Depends(check_current_user_for_admin),
        Depends(check_curr_user_for_block_status),
    ],
)
async def create_group(
    group_name: GroupNameType,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await create_db_group(group_name, db_session)


@router.get(
    "/group/{group_id}",
    response_model=GroupResponseModel,
    dependencies=[
        Depends(check_current_user_for_admin),
        Depends(check_curr_user_for_block_status),
    ],
)
async def get_group(
    group_id: UUID4, db_session: AsyncSession = Depends(get_async_session)
):
    return await get_db_group(group_id, db_session)


@router.delete(
    "/group/{group_id}",
    response_model=UUID4,
    dependencies=[
        Depends(check_current_user_for_admin),
        Depends(check_curr_user_for_block_status),
    ],
)
async def delete_group(
    group_id: UUID4,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await delete_db_group(group_id, db_session)
