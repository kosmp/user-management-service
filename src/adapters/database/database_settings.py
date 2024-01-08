from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from core.exceptions import DatabaseException
from src.core import settings

Base = declarative_base()

database_url = URL.create(**settings.get_db_creds)

async_engine = create_async_engine(database_url, echo=True, future=True)

async_session = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session() as session:
            yield session
    except Exception:
        await session.rollback()
        raise DatabaseException
    finally:
        await session.close()
