from src.adapters.config.settings import PydanticSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

engine = create_async_engine(f"postgresql+{PydanticSettings.db_engine}://{PydanticSettings.postgres_user}:{PydanticSettings.postgres_user_password}@{PydanticSettings.postgres_host}:{PydanticSettings.postgres_port}/{PydanticSettings.postgres_database_name}")

Base = declarative_base()

@asynccontextmanager
async def get_session():
    try:
        async_session = async_session_generator()

        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


def async_session_generator():
    return sessionmaker(
        engine, class_=AsyncSession
    )
