from abc import ABC, abstractmethod
from src.ports.schemas.group import GroupNameType, GroupResponseModel
from pydantic import UUID4
from typing import Union


class GroupRepository(ABC):
    @abstractmethod
    async def create_group(self, group_name: GroupNameType) -> GroupResponseModel:
        pass

    @abstractmethod
    async def get_group(self, group_id: UUID4) -> Union[GroupResponseModel, None]:
        pass

    @abstractmethod
    async def delete_group(self, group_id: UUID4) -> Union[UUID4, None]:
        pass
