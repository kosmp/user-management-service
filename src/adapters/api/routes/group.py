from fastapi import APIRouter, Depends
from src.ports.schemas.group import GroupResponseModel, CreateGroupModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.database_settings import get_async_session
from src.core.actions.group import get_db_group, delete_db_group, create_db_group

router = APIRouter()


@router.post("/groups", response_model=GroupResponseModel)
async def create_group(
    group_name: CreateGroupModel.group_name,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await create_db_group(group_name, db_session)


@router.get("/groups", response_model=GroupResponseModel)
async def get_group(
    group_id: str, db_session: AsyncSession = Depends(get_async_session)
):
    return await get_db_group(group_id, db_session)


@router.delete("/groups", response_model=str)
async def delete_group(
    group_id: str, db_session: AsyncSession = Depends(get_async_session)
):
    return await delete_db_group(group_id, db_session)
