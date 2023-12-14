import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '..', '.env')
load_dotenv()


class PydanticSettings(BaseSettings):
    postgres_user: str = None
    postgres_user_password: str = None
    postgres_host: str = None
    postgres_port: int = None
    postgres_database_name: str = None
    db_engine: str = None

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")
