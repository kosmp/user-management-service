from pydantic import BaseModel, constr, UUID5
from ports.enums import Role
from typing import Optional


class ValidatedEmail(BaseModel):
    email: constr(regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ValidatedPassword(BaseModel):
    password: constr(min_length=8, max_length=15)


class ValidatedName(BaseModel):
    name: constr(min_length=1, max_length=15)


class ValidatedPhoneNumber(BaseModel):
    phone_number: constr(regex=r"^\+?[1-9]\d{1,14}$")


class UserUpdateData(BaseModel):
    email: Optional[ValidatedEmail.email]
    name: Optional[ValidatedName.name]
    surname: Optional[ValidatedName.name]
    password: Optional[ValidatedPassword.password]
    phone_number: Optional[ValidatedPhoneNumber.phone_number]
    role: Optional[Role]
    group_id: Optional[UUID5]
    image: Optional[str]
    is_blocked: Optional[bool]
