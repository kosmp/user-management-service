from fastapi import HTTPException
from pydantic import UUID5
from sqlalchemy.ext.asyncio import AsyncSession
from src.ports.schemas.group import GroupResponseModel, CreateGroupModel
from src.adapters.database.repositories.sqlalchemy_group_repository import (
    SQLAlchemyGroupRepository,
)


async def create_db_group(
    group_name: CreateGroupModel.group_name, db_session: AsyncSession
) -> GroupResponseModel:
    return await SQLAlchemyGroupRepository(db_session).create_group(group_name)


async def get_db_group(group_id: UUID5, db_session: AsyncSession) -> GroupResponseModel:
    return await SQLAlchemyGroupRepository(db_session).get_group(group_id)


async def delete_db_group(group_id: UUID5, db_session: AsyncSession) -> UUID5:
    return await SQLAlchemyGroupRepository(db_session).delete_group(group_id)
