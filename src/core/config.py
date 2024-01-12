from pydantic_settings import BaseSettings


class PydanticSettings(BaseSettings):
    db_driver_name: str = None
    db_username: str = None
    db_password: str = None
    db_host: str = None
    db_port: str = None
    db_database_name: str = None
    redis_host: str = None
    redis_port: int = None
    redis_password: str = None
    secret_key: str = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    rabbitmq_default_user: str = None
    rabbitmq_default_pass: str = None

    @property
    def get_db_creds(self):
        return {
            "drivername": self.db_driver_name,
            "username": self.db_username,
            "host": self.db_host,
            "port": self.db_port,
            "database": self.db_database_name,
            "password": self.db_password,
        }
