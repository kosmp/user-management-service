from enum import Enum


class Role(Enum):
    USER: str = "user"
    ADMIN: str = "admin"
    MODERATOR: str = "moderator"
