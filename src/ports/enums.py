from enum import StrEnum


class Role(StrEnum):
    USER: str = "user"
    ADMIN: str = "admin"
    MODERATOR: str = "moderator"


class SupportedFileTypes(StrEnum):
    PNG: str = "image/png"
    JPEG: str = "image/jpeg"
