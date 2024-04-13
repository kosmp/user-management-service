from abc import ABC, abstractmethod
from typing import Union, List

from src.ports.schemas.user import (
    UserCreateModel,
    UserUpdateModelWithImage,
    UserResponseModel,
    UserResponseModelWithPassword,
)
from pydantic import UUID4


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user_data: UserCreateModel) -> UserResponseModel:
        pass

    @abstractmethod
    async def get_user(
        self,
        user_id: UUID4 | None,
        email: str | None,
        username: str | None,
        phone_number: str | None,
    ) -> Union[UserResponseModelWithPassword, None]:
        pass

    @abstractmethod
    async def get_users(
        self,
        page: int,
        limit: int,
        filter_by_name: str,
        filter_by_group: str,
        sort_by: str,
        order_by: str,
    ) -> List[UserResponseModel]:
        pass

    @abstractmethod
    async def update_user(
        self, user_id: UUID4, user_data: UserUpdateModelWithImage
    ) -> Union[UserResponseModel, None]:
        pass

    @abstractmethod
    async def update_password(
        self, user_id: UUID4, password: str
    ) -> Union[UserResponseModel, None]:
        pass

    @abstractmethod
    async def delete_user(self, user_id: UUID4) -> Union[UUID4, None]:
        pass
