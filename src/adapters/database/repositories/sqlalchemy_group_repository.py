from sqlalchemy import select, delete

from adapters.database.models.groups import Group
from app.exceptions import DatabaseConnectionException
from ports.repositories.group_repository import GroupRepository
from sqlalchemy.orm import Session
from ports.schemas.group import CreateGroupModel
from pydantic import UUID5
from typing import Union


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_group(self, group_name: CreateGroupModel.group_name) -> Group:
        try:
            new_group = Group(name=group_name)

            self.db_session.add(new_group)
            await self.db_session.commit()

            return new_group
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException

    async def get_group(self, group_id: UUID5) -> Union[Group, None]:
        try:
            query = select(Group).where(Group.id == group_id)
            res = await self.db_session.execute(query).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            raise DatabaseConnectionException

    async def delete_group(self, group_id: UUID5) -> bool:
        try:
            query = delete(Group).where(Group.id == group_id)
            res = await self.db_session.execute(query).fetchone()

            if res is None:
                return False
            return True
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException
