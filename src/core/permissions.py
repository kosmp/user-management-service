from fastapi import Security, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4

from src.logging_config import logger
from src.ports.enums import Role
from src.core.services.token import get_token_payload
from src.core import security


def check_current_user_for_admin(
    token: HTTPAuthorizationCredentials = Security(security),
) -> bool:
    current_user_role = get_token_payload(token.credentials).role

    if current_user_role != Role.ADMIN:
        logger.error(
            f"Current user with role {current_user_role} is not allowed to access this."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with the {current_user_role} role does not have access. You are not {Role.ADMIN}.",
        )

    return True


async def check_current_user_for_moderator_and_admin(
    group_id: UUID4, token: str
) -> bool:
    role = get_token_payload(token).role

    if role == Role.ADMIN:
        return True
    elif role == Role.MODERATOR:
        group_id_current_user_belongs_to = get_token_payload(token).group_id
        if str(group_id) != group_id_current_user_belongs_to:
            logger.error(
                f"User with role {role} is not allowed to access this. Must belongs to group with {group_id_current_user_belongs_to}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with the {role} role does not have access. Belong to different groups.",
            )
        else:
            return True
    else:
        logger.error(f"Current user with role {role} is not allowed to access this.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with the {role} role does not have access. You are not {Role.ADMIN} or {Role.MODERATOR}.",
        )


def check_curr_user_for_block_status(
    token: HTTPAuthorizationCredentials = Security(security),
) -> bool:
    if get_token_payload(token.credentials).is_blocked:
        logger.error(f"Current user is blocked.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are blocked."
        )

    return True
