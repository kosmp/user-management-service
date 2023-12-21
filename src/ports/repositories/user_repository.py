from abc import ABC, abstractmethod
from typing import Union

from ports.schemas.user import (
    UserCreateModel,
    UserUpdateModel,
    UserResponseModel,
)
from pydantic import UUID5


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_data: UserCreateModel) -> UserResponseModel:
        pass

    @abstractmethod
    async def get_user(self, user_id: UUID5) -> Union[UserResponseModel, None]:
        pass

    @abstractmethod
    async def update_user(
        self, user_id: UUID5, user_data: UserUpdateModel
    ) -> Union[UserResponseModel, None]:
        pass

    @abstractmethod
    async def block_user(self, user_id: UUID5) -> Union[UserResponseModel, None]:
        pass
