from pydantic import BaseModel, constr, UUID5
from src.ports.enums import Role
from typing import Optional


class UserBase(BaseModel):
    name: constr(min_length=1, max_length=15)
    surname: constr(min_length=1, max_length=15)
    email: constr(regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    phone_number: constr(regex=r"^\+?[1-9]\d{1,14}$")
    is_blocked: bool
    image: str


class UserCreateModel(UserBase):
    password: str
    group_id: UUID5
    role: Role = Role.USER


class UserUpdateModel(UserBase):
    email: Optional[UserBase.email]
    name: Optional[UserBase.name]
    surname: Optional[UserBase.surname]
    phone_number: Optional[UserBase.phone_number]
    image: Optional[UserBase.image]
    is_blocked: Optional[UserBase.is_blocked]
    role: Optional[Role]
    group_id: Optional[UUID5]


class UserResponseModel(UserBase):
    group_id: UUID5
    role: Role
