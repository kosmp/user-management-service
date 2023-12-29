from datetime import datetime

from pydantic import BaseModel, constr, UUID5, EmailStr, field_validator
from src.ports.enums import Role
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[constr(min_length=1, max_length=15)]
    surname: Optional[constr(min_length=1, max_length=15)]
    phone_number: Optional[constr(pattern=r"^\+?[1-9]\d{1,14}$")]
    is_blocked: Optional[bool]
    image: Optional[str]


class UserCreateModel(UserBase):
    password: str
    group_id: UUID5
    role: Role = Role.USER


class SignUpModel(UserBase):
    password: constr(min_length=8)
    group_id: UUID5
    role: Role = Role.USER

    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value


class CredentialsModel(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value


class UserResponseModel(UserBase):
    id: UUID5
    group_id: UUID5
    role: Role
    created_at: datetime


class UserUpdateModel(BaseModel):
    email: Optional[EmailStr]
    name: Optional[constr(min_length=1, max_length=15)]
    surname: Optional[constr(min_length=1, max_length=15)]
    phone_number: Optional[constr(pattern=r"^\+?[1-9]\d{1,14}$")]
    image: Optional[str]
    is_blocked: Optional[bool]
    role: Optional[Role]
    group_id: Optional[UUID5]


class TokenData(BaseModel):
    user_id: UUID5 or None = None
