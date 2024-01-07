from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.services.user import login_user, create_user
from src.ports.schemas.user import SignUpModel, UserResponseModel, CredentialsModel
from src.adapters.database.database_settings import get_async_session
from src.core import oauth2_scheme


router = APIRouter()


@router.post("/auth/signup", response_model=UserResponseModel)
async def signup(
    user_data: SignUpModel, db_session: AsyncSession = Depends(get_async_session)
):
    return await create_user(user_data, db_session)


@router.post("/auth/login")
async def login(
    credentials: CredentialsModel, db_session: AsyncSession = Depends(get_async_session)
):
    return await login_user(credentials, db_session)


@router.post("/auth/refresh-token")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    pass


@router.post("/auth/refresh-password")
async def refresh_password(credentials: CredentialsModel):
    pass
