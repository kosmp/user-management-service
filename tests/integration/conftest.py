import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.adapters.database.database_settings import get_async_session
from src.main import app
from src.adapters.database.models.groups import Group
from src.adapters.database.models.users import User
from src.core import settings


@pytest.fixture(scope="function")
def engine():
    db_url = URL.create(**settings.get_db_creds)
    engine = create_async_engine(db_url, poolclass=NullPool)
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def create(engine):
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.drop_all)
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Group.metadata.drop_all)
        await conn.run_sync(Group.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def get_test_async_session(engine, create):
    async with AsyncSession(engine) as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_client(get_test_async_session):
    async def _get_test_session():
        try:
            yield get_test_async_session
        except Exception as e:
            print(e)

    app.dependency_overrides[get_async_session] = _get_test_session
    url = f"{settings.http_schema}://{settings.host}:{settings.port}"
    async with AsyncClient(app=app, base_url=url) as client:
        yield client


@pytest.fixture()
def test_user_dict_1():
    return dict(
        email="example@mail.ru",
        username="example",
        phone_number="12345",
        name="Example",
        surname="Example",
        password="1234567Psg",
        group_id=None,
        group_name="example",
    )
