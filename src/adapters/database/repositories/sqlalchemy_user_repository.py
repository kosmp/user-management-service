from fastapi import HTTPException, status
from pydantic import UUID5
from sqlalchemy import select, update, delete, asc, desc
from datetime import datetime, timezone

from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
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
from src.core.exceptions import DatabaseException, InvalidRequestException
from typing import Union, List
from pydantic import EmailStr


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
        except IntegrityError as integrity_err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Group with email '{user_data.email}' already exists.",
            )
        except OperationalError as op_err:
            await self.db_session.rollback()
            raise DatabaseException
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as generic_err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the user.",
            )

    async def get_user(self, **kwargs) -> Union[UserResponseModel, None]:
        try:
            user_id = kwargs.get("id")
            email = kwargs.get("email")

            if user_id:
                query = select(User).where(User.id == user_id)
            elif email:
                query = select(User).where(User.email == email)
            else:
                raise InvalidRequestError

            res = (await self.db_session.execute(query)).fetchone()

            if res is not None:
                return UserResponseModel(**res[0].dict())
        except OperationalError as op_err:
            await self.db_session.rollback()
            raise DatabaseException
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

            users = (await self.db_session.execute(query)).all()
            res = [UserResponseModel(**user.dict()) for user in users]
            return res
        except OperationalError as op_err:
            await self.db_session.rollback()
            raise DatabaseException
        except AttributeError:
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
        except OperationalError as op_err:
            await self.db_session.rollback()
            raise DatabaseException
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
        except OperationalError as op_err:
            await self.db_session.rollback()
            raise DatabaseException
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the user.",
            )

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
        except OperationalError as op_err:
            await self.db_session.rollback()
            raise DatabaseException
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while blocking the user.",
            )

    async def delete_user(self, user_id: UUID5) -> Union[UUID5, None]:
        try:
            query = delete(User).where(User.id == user_id).returning(User.id)

            res = (await self.db_session.execute(query)).fetchone()
            if res is not None:
                return res[0]
        except OperationalError as op_err:
            await self.db_session.rollback()
            raise DatabaseException
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
