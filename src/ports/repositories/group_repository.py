from abc import ABC, abstractmethod
from src.ports.schemas.group import GroupNameType
from pydantic import UUID4
from src.adapters.database.models.groups import Group
from typing import Union


class GroupRepository(ABC):
    @abstractmethod
    async def create_group(self, group_name: GroupNameType) -> Group:
        pass

    @abstractmethod
    async def get_group(self, group_id: UUID4) -> Union[Group, None]:
        pass

    @abstractmethod
    async def delete_group(self, group_id: UUID4) -> Union[UUID4, None]:
        pass
