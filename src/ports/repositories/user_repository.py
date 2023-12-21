from abc import ABC, abstractmethod
from typing import Union

from ports.schemas.user import (
    UserCreateModel,
    UserUpdateModel,
)
from pydantic import UUID5
from adapters.database.models.users import User


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_data: UserCreateModel) -> User:
        pass

    @abstractmethod
    async def get_user(self, user_id: UUID5) -> Union[User, None]:
        pass

    @abstractmethod
    async def update_user(
        self, user_id: UUID5, user_data: UserUpdateModel
    ) -> Union[User, None]:
        pass

    @abstractmethod
    async def block_user(self, user_id: UUID5) -> bool:
        pass
