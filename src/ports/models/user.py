from pydantic import BaseModel, constr
from ports.enums import Role
from typing import Optional


class ValidatedEmail(BaseModel):
    email: constr(regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ValidatedPassword(BaseModel):
    password: constr(min_length=8, max_length=15)


class UserUpdateData(BaseModel):
    email: Optional[ValidatedEmail]
    name: Optional[constr(min_length=1, max_length=15)]
    surname: Optional[constr(min_length=1, max_length=15)]
    password: Optional[ValidatedPassword]
    phone_number: Optional[constr(regex=r"^\+?[1-9]\d{1,14}$")]
    role: Optional[Role]
    group_id: Optional[int]
    image: Optional[str]
    is_blocked: Optional[bool]
