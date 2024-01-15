from fastapi import HTTPException, status
from pydantic import UUID4, EmailStr
from sqlalchemy import select, update, delete, asc, desc
from datetime import datetime

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
    UserResponseModelWithPassword,
)
from src.adapters.database.models.users import User
from src.core.exceptions import InvalidRequestException
from typing import Union, List


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreateModel) -> UserResponseModel:
        try:
            new_user = User(
                **user_data.model_dump(exclude_none=True, exclude_unset=True)
            )

            self.db_session.add(new_user)
            await self.db_session.commit()

            return UserResponseModel.model_validate(new_user)
        except IntegrityError as integrity_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User already exists.",
            )
        except InvalidRequestError as inv_req_err:
            raise InvalidRequestException
        except Exception as generic_err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the user.",
            )

    async def get_user(
        self,
        user_id: UUID4 | None = None,
        email: EmailStr | None = None,
        username: str | None = None,
    ) -> UserResponseModelWithPassword:
        try:
            if user_id:
                query = select(User).where(User.id == str(user_id))
            elif username:
                query = select(User).where(User.id == username)
            elif email:
                query = select(User).where(User.email == str(email))
            else:
                raise InvalidRequestError

            res = await self.db_session.scalar(query)

            if res is not None:
                return res
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
        filter_by_group_id: str = None,
        sort_by: str = None,
        order_by: str = "asc",
    ) -> List[UserResponseModel]:
        try:
            query = select(User)

            if filter_by_group_id is not None:
                query = query.where(User.group_id.ilike(f"%{filter_by_group_id}"))

            if filter_by_name is not None:
                query = query.where(User.name.ilike(f"%{filter_by_name}%"))

            if sort_by is not None:
                column_to_sort = getattr(User, sort_by)
                if order_by == "asc":
                    query = query.order_by(asc(column_to_sort))
                elif order_by == "desc":
                    query = query.order_by(desc(column_to_sort))

            query = query.limit(limit).offset((page - 1) * limit)

            users = await self.db_session.scalars(query)
            return users.all()
        except AttributeError as attr_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid attributes.",
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
                .where(User.id == str(user_id))
                .values(**user_data.model_dump(exclude_none=True, exclude_unset=True))
                .returning(User)
            )
            res = (await self.db_session.execute(query)).scalar_one_or_none()
            await self.db_session.commit()

            return res
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
                .values(password)
                .returning(User)
            )
            res = (await self.db_session.execute(query)).scalar_one_or_none()
            await self.db_session.commit()

            return res
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the user.",
            )

    async def delete_user(self, user_id: UUID4) -> Union[UUID4, None]:
        try:
            query = delete(User).where(User.id == str(user_id)).returning(User.id)
            res = await self.db_session.scalar(query)
            await self.db_session.commit()

            if res is not None:
                return res
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
            raise InvalidRequestError
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the user.",
            )
