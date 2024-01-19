from sqlalchemy import select, delete, UUID
from fastapi import HTTPException, status
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    NoResultFound,
)

from src.adapters.database.models.groups import Group
from src.ports.repositories.group_repository import GroupRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.ports.schemas.group import GroupNameType, GroupResponseModel
from src.core.exceptions import InvalidRequestException
from pydantic import UUID4
from typing import Union


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_group(self, group_name: GroupNameType) -> GroupResponseModel:
        try:
            new_group = Group(name=group_name)

            self.db_session.add(new_group)
            await self.db_session.flush()

            return GroupResponseModel.model_validate(new_group)
        except IntegrityError as integrity_err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Group with name '{group_name}' already exists.",
            )
        except InvalidRequestError as inv_req_err:
            await self.db_session.rollback()
            raise InvalidRequestException
        except Exception as generic_err:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the group.",
            )

    async def get_group(self, group_id: UUID4) -> Union[GroupResponseModel, None]:
        try:
            query = select(Group).where(Group.id == str(group_id))
            res = await self.db_session.scalar(query)

            if res is not None:
                return GroupResponseModel(
                    id=res.id, name=res.name, created_at=res.created_at
                )
            else:
                raise NoResultFound
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found.",
            )
        except InvalidRequestError as inv_req_err:
            raise InvalidRequestException
        except Exception as generic_err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while retrieving the group.",
            )

    async def delete_group(self, group_id: UUID4) -> Union[UUID4, None]:
        try:
            query = delete(Group).where(Group.id == str(group_id)).returning(Group.id)
            res = await self.db_session.scalar(query)
            await self.db_session.commit()

            if res is not None:
                return res
            else:
                raise NoResultFound
        except IntegrityError as int_err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the group due to integrity constraints.",
            )
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found.",
            )
        except InvalidRequestError as inv_req_err:
            raise InvalidRequestError
        except Exception as err:
            raise HTTPException(
                status_code=500, detail="An error occurred while deleting the group."
            )
