from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.permissions import check_curr_user_for_block_status
from src.core.actions.user import create_user, login_user, get_refresh_token
from src.ports.schemas.user import (
    SignUpModel,
    UserResponseModel,
    CredentialsModel,
    PasswordModel,
    TokensResult,
)
from src.adapters.database.database_settings import get_async_session
from src.core.actions.user import request_reset_user_password, reset_user_password


router = APIRouter()


@router.post("/auth/signup", response_model=UserResponseModel)
async def signup(
    user_data: SignUpModel = Depends(),
    image_file: Annotated[UploadFile, File()] = None,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await create_user(user_data, db_session, image_file)


@router.post("/auth/login", response_model=TokensResult)
async def login(
    credentials: CredentialsModel,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await login_user(
        credentials,
        db_session,
    )


@router.post("/auth/refresh-token", response_model=TokensResult)
async def refresh_token(
    token: str,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await get_refresh_token(token, db_session)


@router.post("/auth/request-password-reset")
async def request_reset_password(
    email: EmailStr, db_session: AsyncSession = Depends(get_async_session)
):
    return await request_reset_user_password(email, db_session)


@router.put("/auth/reset-password", response_model=UserResponseModel)
async def reset_password(
    new_password: PasswordModel,
    token: str,
    db_session: AsyncSession = Depends(get_async_session),
):
    return await reset_user_password(token, new_password, db_session)
