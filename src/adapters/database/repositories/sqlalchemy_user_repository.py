from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy import select, update, delete, asc, desc, UUID
from datetime import datetime, timezone

from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    NoResultFound,
)

from src.ports.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.ports.schemas.user import (
    UserUpdateModel,
    UserCreateModel,
    UserResponseModel,
)
from src.adapters.database.models.users import User
from src.core.exceptions import InvalidRequestException
from typing import Union, List


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreateModel) -> UserResponseModel:
        try:
            new_user = User(**user_data.model_dump())

            self.db_session.add(new_user)
            await self.db_session.commit()

            return UserResponseModel(**new_user.__dict__)
        except IntegrityError as integrity_err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"User with email '{user_data.email}' already exists.",
            )
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as generic_err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while creating the user.",
            )

    async def get_user(self, **kwargs) -> Union[UserResponseModel, None]:
        try:
            user_id = kwargs.get("id")
            email = kwargs.get("email")

            if user_id:
                query = select(User).where(User.id == str(user_id))
            elif email:
                query = select(User).where(User.email == str(email))
            else:
                raise InvalidRequestError

            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return UserResponseModel(
                    id=res[0].id,
                    email=res[0].email,
                    name=res[0].name,
                    surname=res[0].surname,
                    phone_number=res[0].phone_number,
                    is_blocked=res[0].is_blocked,
                    image=res[0].image,
                    group_id=res[0].group_id,
                    role=res[0].role,
                    created_at=res[0].created_at,
                )
            else:
                raise NoResultFound
        except NoResultFound:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as generic_err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving the user.",
            )

    async def get_users(
        self,
        page: int = 1,
        limit: int = 30,
        filter_by_name: str = None,
        sort_by: str = None,
        order_by: str = "asc",
    ) -> List[UserResponseModel]:
        try:
            query = select(User)

            if filter_by_name is not None:
                query = query.where(User.name.ilike(f"%{filter_by_name}%"))

            if sort_by is not None:
                column_to_sort = getattr(User, sort_by)
                if order_by == "asc":
                    query = query.order_by(asc(column_to_sort))
                elif order_by == "desc":
                    query = query.order_by(desc(column_to_sort))

            query = query.limit(limit).offset((page - 1) * limit)

            users = (await self.db_session.execute(query)).fetchall()
            res = [
                UserResponseModel(
                    id=user[0].id,
                    email=user[0].email,
                    name=user[0].name,
                    surname=user[0].surname,
                    phone_number=user[0].phone_number,
                    is_blocked=user[0].is_blocked,
                    image=user[0].image,
                    group_id=user[0].group_id,
                    role=user[0].role,
                    created_at=user[0].created_at,
                )
                for user in users
            ]
            return res
        except AttributeError as attr_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid attributes.",
            )
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving users.",
            )

    async def update_user(
        self, user_id: UUID4, user_data: UserUpdateModel
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
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the user.",
            )

    async def update_password(
        self, user_id: UUID4, password: str
    ) -> Union[UserResponseModel, None]:
        try:
            query = (
                update(User)
                .where(User.id == str(user_id))
                .values(password, modified_at=datetime.now(timezone.utc))
                .returning(User.id)
            )
            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return UserResponseModel(**res[0].dict())
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the user.",
            )

    async def block_user(self, user_id: UUID4) -> Union[UserResponseModel, None]:
        try:
            query = (
                update(User)
                .where(User.id == str(user_id))
                .values(is_blocked=True)
                .returning(User.id)
            )
            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return UserResponseModel(**res[0].dict())
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while blocking the user.",
            )

    async def delete_user(self, user_id: UUID4) -> Union[UUID4, None]:
        try:
            query = delete(User).where(User.id == str(user_id)).returning(User.id)

            res = (await self.db_session.execute(query)).fetchone()
            if res is not None:
                return res[0]
        except NoResultFound:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestError
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the user.",
            )
