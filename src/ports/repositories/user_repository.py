from abc import ABC, abstractmethod
from typing import Union

from ports.models.user import (
    UserUpdateData,
    ValidatedEmail,
    ValidatedPassword,
    ValidatedName,
    ValidatedPhoneNumber,
)
from ports.enums import Role
from pydantic import UUID5
from adapters.database.models.users import User


class UserRepository(ABC):
    @abstractmethod
    async def create_user(
        self,
        email: ValidatedEmail.email,
        name: ValidatedName.name,
        surname: ValidatedName.name,
        phone_number: ValidatedPhoneNumber.phone_number,
        password: ValidatedPassword.password,
        group_id: UUID5,
        role: Role = Role.USER,
    ) -> User:
        pass

    @abstractmethod
    async def get_user(self, user_id: UUID5) -> Union[User, None]:
        pass

    @abstractmethod
    async def update_user(
        self, user_id: UUID5, user_data: UserUpdateData
    ) -> Union[UUID5, None]:
        pass

    @abstractmethod
    async def delete_user(self, user_id: UUID5) -> bool:
        pass
