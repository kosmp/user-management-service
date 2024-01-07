from src.ports.schemas.user import SignUpModel
from src.core.services.hasher import PasswordHasher
from src.ports.schemas.user import UserCreateModel
from src.core.actions.user import get_db_user_by_email, create_db_user

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(user_data: SignUpModel, db_session: AsyncSession):
    user_exists = get_db_user_by_email(user_data.email, db_session=db_session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already exists"
        )

    hashed_password = PasswordHasher.get_password_hash(user_data.password)

    new_user = await create_db_user(
        UserCreateModel(
            **user_data.model_dump(
                exclude={"password"}, include={"password": hashed_password}
            )
        ),
        db_session,
    )

    return new_user
