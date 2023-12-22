from fastapi import APIRouter

router = APIRouter()


@router.post("/auth/signup")
async def signup(email: str, password: str):
    pass


@router.post("/auth/login")
async def login(email: str):
    pass


@router.post("/auth/refresh-token")
async def refresh_token(token: str):
    pass


@router.post("/auth/refresh-password")
async def refresh_password(email: str, password: str):
    pass
