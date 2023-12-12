from pydantic import BaseSettings, AnyUrl

class PydanticSettings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: AnyUrl = None
