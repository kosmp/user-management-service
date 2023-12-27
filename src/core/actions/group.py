from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.ports.schemas.group import GroupResponseModel, CreateGroupModel
from src.adapters.database.repositories.sqlalchemy_group_repository import (
    SQLAlchemyGroupRepository,
)


async def create_db_group(
    group_name: CreateGroupModel.group_name, db_session: AsyncSession
) -> GroupResponseModel:
    db_group = await SQLAlchemyGroupRepository(db_session).create_group(group_name)

    if db_group is None:
        raise HTTPException(status_code=500, detail="Group wasn't created")
    return db_group


async def get_db_group(group_id: str, db_session: AsyncSession) -> GroupResponseModel:
    db_group = await SQLAlchemyGroupRepository(db_session).get_group(group_id)

    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group


async def delete_db_group(group_id: str, db_session: AsyncSession) -> str:
    deleted_group_id = await SQLAlchemyGroupRepository(db_session).delete_group(
        group_id
    )

    if deleted_group_id is None:
        raise HTTPException(status_code=422, detail="Group can't be deleted")

    return deleted_group_id
