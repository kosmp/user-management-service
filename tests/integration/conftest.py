import json

import pytest
import pytest_asyncio
from httpx import AsyncClient, Response
from sqlalchemy import NullPool
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from ports.schemas.user import SignUpModel, CredentialsModel
from src.adapters.database.database_settings import get_async_session
from src.main import app
from src.adapters.database.models.groups import Group
from src.adapters.database.models.users import User
from src.core import settings


def serialize(binary: bytes):
    return json.loads(binary.decode("utf-8"))


@pytest.fixture(scope="function")
def engine():
    db_url = URL.create(**settings.get_db_creds)
    engine = create_async_engine(db_url, poolclass=NullPool)
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def refresh_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.drop_all)
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Group.metadata.drop_all)
        await conn.run_sync(Group.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def get_test_async_session(engine, refresh_tables):
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


@pytest.fixture()
def test_user_dict_2():
    return dict(
        email="test@mail.ru",
        username="example1",
        phone_number="123451",
        name="Example",
        surname="Example",
        password="1234567Psg",
        group_id=None,
        group_name="test group 1",
    )


@pytest.fixture()
def test_user_dict_3():
    return dict(
        email="test@mail.ru",
        username="example2",
        phone_number="123452",
        name="Example",
        surname="Example",
        password="1234567Psg",
        group_id=None,
        group_name="test group 2",
    )


@pytest.fixture()
def test_user_dict_4():
    return dict(
        email="abcde@mail.ru",
        username="abcde",
        phone_number="66666",
        name="Example",
        surname="Example",
        password="1234567Psg",
        group_id=None,
        group_name="test group 3",
    )


@pytest_asyncio.fixture(scope="function")
async def login_success(
    test_client: AsyncClient, test_user_dict_4, refresh_tables
) -> Response:
    signup_data = SignUpModel(**test_user_dict_4)
    login_data = CredentialsModel(
        login=test_user_dict_4.get("username"),
        password=test_user_dict_4.get("password"),
    )

    await test_client.post("/v1/auth/signup", data=signup_data.__dict__)
    return await test_client.post("/v1/auth/login", json=login_data.model_dump())
