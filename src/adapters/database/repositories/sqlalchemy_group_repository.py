from sqlalchemy import select, delete
from fastapi import HTTPException
from src.adapters.database.models.groups import Group
from src.ports.repositories.group_repository import GroupRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.ports.schemas.group import CreateGroupModel
from pydantic import UUID5
from typing import Union


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_group(self, group_name: CreateGroupModel.group_name) -> Group:
        try:
            new_group = Group(name=group_name)

            self.db_session.add(new_group)
            await self.db_session.commit()

            return new_group
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500, detail="An error occurred while creating the group"
            )

    async def get_group(self, group_id: UUID5) -> Union[Group, None]:
        try:
            query = select(Group).where(Group.id == group_id)
            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            raise HTTPException(
                status_code=500, detail="An error occurred while retrieving the group"
            )

    async def delete_group(self, group_id: UUID5) -> Union[UUID5, None]:
        try:
            query = delete(Group).where(Group.id == group_id).returning(Group.id)
            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=500, detail="An error occurred while deleting the group"
            )
