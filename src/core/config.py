from pydantic_settings import BaseSettings


class PydanticSettings(BaseSettings):
    db_driver_name: str = None
    db_username: str = None
    db_password: str = None
    db_host: str = None
    db_port: str = None
    db_database_name: str = None

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
