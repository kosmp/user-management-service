from dataclasses import dataclass
from datetime import datetime

from fastapi import UploadFile, Form
from pydantic import (
    BaseModel,
    constr,
    UUID4,
    EmailStr,
    field_validator,
    ConfigDict,
    Field,
)

from src.ports.schemas.group import GroupNameType
from src.ports.enums import Role
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str
    phone_number: constr(pattern=r"^\+?[1-9]\d{1,14}$")
    name: Optional[constr(min_length=1, max_length=15)] = None
    surname: Optional[constr(min_length=1, max_length=15)] = None


class UserCreateModel(UserBase):
    image: Optional[str] = None
    password: str
    group_id: UUID4
    role: Optional[Role] = Role.USER


@dataclass
class SignUpModel:
    email: EmailStr = Form()
    username: str = Form()
    phone_number: str = Form(pattern=r"^\+?[1-9]\d{1,14}$")
    name: Optional[str] = Form(min_length=1, max_length=15, default=None)
    surname: Optional[str] = Form(min_length=1, max_length=15, default=None)
    password: str = Form(min_length=8)
    group_id: Optional[UUID4] = Form(default=None)
    group_name: Optional[GroupNameType] = Form(default=None)

    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value


class PasswordModel(BaseModel):
    password: constr(min_length=8)

    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value


class CredentialsModel(PasswordModel):
    login: str


class UserResponseModel(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    group_id: UUID4
    role: Role
    created_at: datetime
    image: str
    is_blocked: bool
    modified_at: Optional[datetime] = None


class UserResponseModelWithPassword(UserResponseModel):
    password: str


class UserUpdateModelWithoutImage(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    name: Optional[constr(min_length=1, max_length=15)] = None
    surname: Optional[constr(min_length=1, max_length=15)] = None
    phone_number: Optional[constr(pattern=r"^\+?[1-9]\d{1,14}$")] = None
    image: Optional[str] = None
    is_blocked: Optional[bool] = None
    role: Optional[Role] = None
    group_id: Optional[UUID4] = None


class UserUpdateModelWithImage(UserUpdateModelWithoutImage):
    image: Optional[str] = None


@dataclass
class UserUpdateRequestModelWithoutImage:
    email: Optional[EmailStr] = Form()
    username: Optional[str] = Form()
    phone_number: Optional[str] = Form(pattern=r"^\+?[1-9]\d{1,14}$")
    name: Optional[str] = Form(min_length=1, max_length=15, default=None)
    surname: Optional[str] = Form(min_length=1, max_length=15, default=None)
    group_id: Optional[UUID4] = Form(default=None)
    is_blocked: Optional[bool] = Form(default=None)
    role: Optional[Role] = Form(default=None)


@dataclass
class UserUpdateMeRequestModel:
    email: Optional[EmailStr] = Form()
    username: Optional[str] = Form()
    phone_number: Optional[str] = Form(pattern=r"^\+?[1-9]\d{1,14}$")
    name: Optional[str] = Form(min_length=1, max_length=15, default=None)
    surname: Optional[str] = Form(min_length=1, max_length=15, default=None)
    group_id: Optional[UUID4] = Form(default=None)


class TokenData(BaseModel):
    user_id: str
    role: str
    group_id: str
    is_blocked: bool


class TokensResult(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
