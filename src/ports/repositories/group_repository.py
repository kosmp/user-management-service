from abc import ABC, abstractmethod
from src.ports.schemas.group import CreateGroupModel
from pydantic import UUID5
from src.adapters.database.models.groups import Group
from typing import Union


class GroupRepository(ABC):
    @abstractmethod
    async def create_group(self, group_name: CreateGroupModel.group_name) -> Group:
        pass

    @abstractmethod
    async def get_group(self, group_id: UUID5) -> Union[Group, None]:
        pass

    @abstractmethod
    async def delete_group(self, group_id: UUID5) -> Union[Group, None]:
        pass
