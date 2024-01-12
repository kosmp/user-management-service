from datetime import datetime

from pydantic import BaseModel, constr, UUID4, EmailStr, field_validator

from src.ports.schemas.group import GroupNameType
from src.ports.enums import Role
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[constr(min_length=1, max_length=15)] = None
    surname: Optional[constr(min_length=1, max_length=15)] = None
    phone_number: Optional[constr(pattern=r"^\+?[1-9]\d{1,14}$")] = None
    is_blocked: Optional[bool] = None
    image: Optional[str] = None


class UserCreateModel(UserBase):
    password: str
    group_id: UUID4
    role: Role = Role.USER


class SignUpModel(UserBase):
    password: constr(min_length=8)
    group_id: Optional[UUID4] = None
    group_name: Optional[GroupNameType] = None
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
    id: UUID4
    group_id: UUID4
    role: Role
    created_at: datetime
    modified_at: Optional[datetime] = None


class UserResponseModelWithPassword(UserResponseModel):
    password: str


class UserUpdateModel(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[constr(min_length=1, max_length=15)] = None
    surname: Optional[constr(min_length=1, max_length=15)] = None
    phone_number: Optional[constr(pattern=r"^\+?[1-9]\d{1,14}$")] = None
    image: Optional[str] = None
    is_blocked: Optional[bool] = None
    role: Optional[Role] = None
    group_id: Optional[UUID4] = None


class TokenData(BaseModel):
    user_id: str
    role: str
    group_id_user_belongs_to: str
