from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4

from src.core import security
from src.ports.schemas.group import GroupResponseModel, CreateGroupModel, GroupNameType
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.database_settings import get_async_session
from src.core.actions.group import get_db_group, delete_db_group, create_db_group

router = APIRouter()


@router.post("/group", response_model=GroupResponseModel)
async def create_group(
    group_name: GroupNameType,
    db_session: AsyncSession = Depends(get_async_session),
    token: HTTPAuthorizationCredentials = Security(security),
):
    return await create_db_group(group_name, db_session)


@router.get("/group/{group_id}", response_model=GroupResponseModel)
async def get_group(
    group_id: UUID4,
    db_session: AsyncSession = Depends(get_async_session),
    token: HTTPAuthorizationCredentials = Security(security),
):
    return await get_db_group(group_id, db_session)


@router.delete("/group/{group_id}", response_model=UUID4)
async def delete_group(
    group_id: UUID4,
    db_session: AsyncSession = Depends(get_async_session),
    token: HTTPAuthorizationCredentials = Security(security),
):
    return await delete_db_group(group_id, db_session)
