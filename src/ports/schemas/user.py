from pydantic import BaseModel, constr, UUID5
from ports.enums import Role
from typing import Optional


class UserBase(BaseModel):
    name: constr(min_length=1, max_length=15)
    surname: constr(min_length=1, max_length=15)
    email: constr(regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    phone_number: constr(regex=r"^\+?[1-9]\d{1,14}$")
    password: constr(min_length=8, max_length=15)


class UserCreateModel(UserBase):
    group_id: UUID5
    role: Role = Role.USER


class UserUpdateModel(UserBase):
    email: Optional[UserBase.email]
    name: Optional[UserBase.name]
    surname: Optional[UserBase.surname]
    password: Optional[UserBase.password]
    phone_number: Optional[UserBase.phone_number]
    role: Optional[Role]
    group_id: Optional[UUID5]
    image: Optional[str]
    is_blocked: Optional[bool]
