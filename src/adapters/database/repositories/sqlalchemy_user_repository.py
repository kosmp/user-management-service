from pydantic import UUID5
from sqlalchemy import select, update
from datetime import datetime, timezone
from app.exceptions import DatabaseConnectionException
from ports.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from ports.schemas.user import UserUpdateModel, UserCreateModel
from adapters.database.models.users import User
from typing import Union


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreateModel) -> User:
        try:
            new_user = User(
                email=user_data.email,
                password=user_data.password,
                group_id=user_data.group_id,
                role=user_data.role,
            )

            self.db_session.add(new_user)
            await self.db_session.commit()

            return new_user
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException

    async def get_user(self, user_id: UUID5) -> Union[User, None]:
        try:
            query = select(User).where(User.id == user_id)
            res = await self.db_session.execute(query).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            raise DatabaseConnectionException

    async def update_user(
        self, user_id: UUID5, user_data: UserUpdateModel
    ) -> Union[User, None]:
        try:
            query = (
                update(User)
                .where(User.is_blocked == False)
                .values(**user_data, modified_at=datetime.now(timezone.utc))
            )
            res = await self.db_session.execute(query).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException

    async def block_user(self, user_id: UUID5) -> Union[User, None]:
        try:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(is_blocked=True)
                .returning(User.id)
            )
            res = await self.db_session.execute(query).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException
