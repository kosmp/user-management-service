from fastapi import APIRouter
from src.ports.schemas.user import SignUpModel, UserResponseModel, CredentialsModel

router = APIRouter()


@router.post("/auth/signup", response_model=UserResponseModel)
async def signup(user_data: SignUpModel):
    pass


@router.post("/auth/login")
async def login(credentials: CredentialsModel):
    pass


@router.post("/auth/refresh-token")
async def refresh_token():
    pass


@router.post("/auth/refresh-password")
async def refresh_password(credentials: CredentialsModel):
    pass
