from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from src.ports.schemas.group import GroupResponseModel, CreateGroupModel, GroupNameType
from src.adapters.database.repositories.sqlalchemy_group_repository import (
    SQLAlchemyGroupRepository,
)


async def create_db_group(
    group_name: GroupNameType, db_session: AsyncSession
) -> GroupResponseModel:
    group = await SQLAlchemyGroupRepository(db_session).create_group(group_name)
    await db_session.commit()

    return group


async def get_db_group(group_id: UUID4, db_session: AsyncSession) -> GroupResponseModel:
    group = await SQLAlchemyGroupRepository(db_session).get_group(group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )
    return group


async def delete_db_group(group_id: UUID4, db_session: AsyncSession) -> UUID4:
    return await SQLAlchemyGroupRepository(db_session).delete_group(group_id)
