from pydantic import UUID5
from sqlalchemy import select, update, and_
from datetime import datetime, timezone
from ports.enums import Role
from app.exceptions import DatabaseConnectionException
from ports.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from ports.models.user import (
    UserUpdateData,
    ValidatedEmail,
    ValidatedPassword,
    ValidatedName,
    ValidatedPhoneNumber,
)
from adapters.database.models.users import User
from typing import Union


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(
        self,
        email: ValidatedEmail.email,
        name: ValidatedName.name,
        surname: ValidatedName.name,
        password: ValidatedPassword.password,
        phone_number: ValidatedPhoneNumber.phone_number,
        group_id: UUID5,
        role: Role = Role.USER,
    ) -> User:
        try:
            new_user = User(
                email=email, password=password, group_id=group_id, role=role
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
        self, user_id: UUID5, user_data: UserUpdateData
    ) -> Union[UUID5, None]:
        try:
            query = (
                update(User)
                .where(User.is_blocked == False)
                .values(**user_data, modified_at=datetime.now(timezone.utc))
                .returning(User.id)
            )
            res = await self.db_session.execute(query).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException

    async def delete_user(self, user_id: UUID5) -> Union[User, None]:
        try:
            query = (
                update(User)
                .where(and_(User.id == user_id, User.is_blocked == False))
                .values(is_blocked=True)
                .returning(User.id)
            )
            res = await self.db_session.execute(query).fetchone()

            if res is not None:
                return res[0]
        except Exception as err:
            await self.db_session.rollback()
            raise DatabaseConnectionException
