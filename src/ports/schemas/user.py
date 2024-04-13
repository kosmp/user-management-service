from dataclasses import dataclass
from datetime import datetime

from fastapi import Form
from pydantic import (
    BaseModel,
    constr,
    UUID4,
    EmailStr,
    field_validator,
    ConfigDict,
)

from src.ports.schemas.group import GroupNameType, GroupResponseModel
from src.ports.enums import Role, TokenType
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
    username: str = Form(pattern=r"^[a-zA-Z0-9_]+$")
    phone_number: str = Form(pattern=r"^\+?[1-9]\d{1,14}$")
    name: str = Form(min_length=1, max_length=15, default=None)
    surname: str = Form(min_length=1, max_length=15, default=None)
    password: str = Form(min_length=8)
    group_id: UUID4 = Form(default=None)
    group_name: GroupNameType = Form(default=None)

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
    image: Optional[str] = None
    is_blocked: bool
    modified_at: Optional[datetime] = None


class UserResponseModelWithPassword(UserResponseModel):
    password: str


class UserUpdateModelWithoutImage(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(pattern=r"^[a-zA-Z0-9_]+$")] = None
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
    email: EmailStr = Form(default=None)
    username: str = Form(pattern=r"^[a-zA-Z0-9_]+$", default=None)
    phone_number: str = Form(pattern=r"^\+?[1-9]\d{1,14}$", default=None)
    name: str = Form(min_length=1, max_length=15, default=None)
    surname: str = Form(min_length=1, max_length=15, default=None)
    group_id: UUID4 = Form(default=None)
    is_blocked: bool = Form(default=None)
    role: Role = Form(default=None)


@dataclass
class UserUpdateMeRequestModel:
    email: EmailStr = Form(default=None)
    username: str = Form(pattern=r"^[a-zA-Z0-9_]+$", default=None)
    phone_number: str = Form(pattern=r"^\+?[1-9]\d{1,14}$", default=None)
    name: str = Form(min_length=1, max_length=15, default=None)
    surname: str = Form(min_length=1, max_length=15, default=None)
    group_id: UUID4 = Form(default=None)


class TokenData(BaseModel):
    user_id: str
    role: str
    group_id: str
    is_blocked: bool


class TokenDataWithTokenType(TokenData):
    token_type: TokenType


class TokensResult(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
