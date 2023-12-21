from pydantic import BaseModel, constr, UUID5
from ports.enums import Role
from typing import Optional


class UserBase(BaseModel):
    name: constr(min_length=1, max_length=15)
    surname: constr(min_length=1, max_length=15)
    email: constr(regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    phone_number: constr(regex=r"^\+?[1-9]\d{1,14}$")
    is_blocked: bool
    image: str


class UserBaseWithPassword(UserBase):
    password: constr(min_length=8, max_length=15)


class UserCreateModel(UserBaseWithPassword):
    group_id: UUID5
    role: Role = Role.USER


class UserUpdateModel(UserBaseWithPassword):
    email: Optional[UserBaseWithPassword.email]
    name: Optional[UserBaseWithPassword.name]
    surname: Optional[UserBaseWithPassword.surname]
    password: Optional[UserBaseWithPassword.password]
    phone_number: Optional[UserBaseWithPassword.phone_number]
    image: Optional[UserBaseWithPassword.image]
    is_blocked: Optional[UserBaseWithPassword.is_blocked]
    role: Optional[Role]
    group_id: Optional[UUID5]


class UserResponseModel(UserBase):
    group_id: UUID5
    role: Role = Role.USER
