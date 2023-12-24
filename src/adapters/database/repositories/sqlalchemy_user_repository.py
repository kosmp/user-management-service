from pydantic import UUID5
from sqlalchemy import select, update
from datetime import datetime, timezone
from src.core.exceptions import DatabaseConnectionException
from src.ports.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.ports.schemas.user import (
    UserUpdateModel,
    UserCreateModel,
    UserResponseModel,
)
from src.adapters.database.models.users import User
from typing import Union, List


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreateModel) -> UserResponseModel:
        try:
            new_user = User(
                email=user_data.email,
                password=user_data.password,
                group_id=user_data.group_id,
                role=user_data.role,
            )

            self.db_session.add(new_user)
            await self.db_session.commit()

            return UserResponseModel(**new_user.dict())
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException

    async def get_user(self, user_id: UUID5) -> Union[UserResponseModel, None]:
        try:
            query = select(User).where(User.id == user_id)
            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return UserResponseModel(**res[0].dict())
        except Exception as err:
            raise DatabaseConnectionException

    async def get_users(self) -> List[UserResponseModel]:
        try:
            query = select(User)
            users = (await self.db_session.execute(query)).all()
            res = [UserResponseModel(**user.dict()) for user in users]
            return res
        except Exception as err:
            raise DatabaseConnectionException

    async def update_user(
        self, user_id: UUID5, user_data: UserUpdateModel
    ) -> Union[UserResponseModel, None]:
        try:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(
                    **user_data.model_dump(), modified_at=datetime.now(timezone.utc)
                )
                .returning(User.id)
            )
            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return UserResponseModel(**res[0].dict())
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException

    async def update_password(
        self, user_id: UUID5, password: str
    ) -> Union[UserResponseModel, None]:
        try:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(password, modified_at=datetime.now(timezone.utc))
                .returning(User.id)
            )
            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return UserResponseModel(**res[0].dict())
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException

    async def block_user(self, user_id: UUID5) -> Union[UserResponseModel, None]:
        try:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(is_blocked=True)
                .returning(User.id)
            )
            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return UserResponseModel(**res[0].dict())
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException
