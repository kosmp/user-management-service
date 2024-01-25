from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator

from src.logging_config import logger
from src.core import settings

database_url = URL.create(**settings.get_db_creds)

async_engine = create_async_engine(database_url)

async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
