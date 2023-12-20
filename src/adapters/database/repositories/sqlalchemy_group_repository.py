from sqlalchemy import select, delete, and_

from adapters.database.models.groups import Group
from app.exceptions import DatabaseConnectionException
from ports.repositories.group_repository import GroupRepository
from sqlalchemy.orm import Session
from ports.models.group import ValidatedGroupName
from pydantic import UUID5
from typing import Union


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create_group(self, group_name: ValidatedGroupName) -> Group:
        try:
            new_group = Group(name=group_name.name)

            self.db.add(new_group)
            await self.db.commit()

            return new_group
        except Exception as err:
            await self.db.rollback()
            raise DatabaseConnectionException

    async def get_group(self, group_id: UUID5) -> Union[Group, None]:
        try:
            query = select(Group).where(Group.id == group_id)
            res = await self.db.execute(query).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            raise DatabaseConnectionException

    async def delete_group(self, group_id: UUID5) -> Union[Group, None]:
        try:
            query = delete(Group).where(
                and_(Group.id == group_id, len(Group.users) == 0)
            )
            await self.db.execute(query)

            return True
        except Exception as err:
            await self.db.rollback()
            raise DatabaseConnectionException
