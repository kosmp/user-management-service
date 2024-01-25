import json
from datetime import timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient, Response
from sqlalchemy import NullPool
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.core.services.token import generate_token
from src.ports.enums import TokenType, Role
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.adapters.database.repositories.sqlalchemy_group_repository import (
    SQLAlchemyGroupRepository,
)
from src.ports.schemas.user import (
    SignUpModel,
    CredentialsModel,
    UserCreateModel,
    TokenDataWithTokenType,
    UserResponseModel,
)
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
def test_user_sign_up_dict():
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
def test_user_sign_up_dict_2():
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
def test_user_sign_up_dict_3():
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
def test_user_dict_user():
    return dict(
        email="abcde@mail.ru",
        username="abcde",
        phone_number="66666",
        name="Example",
        surname="Example",
        password="1234567Psg",
        group_id=None,
        group_name="test 1",
        role=Role.USER,
    )


@pytest.fixture()
def test_user_dict_admin():
    return dict(
        email="test_user_email@mail.ru",
        username="useruser",
        phone_number="32632",
        name="Example",
        surname="Example",
        password="1234567Psg",
        group_id=None,
        group_name="test 2",
        role=Role.ADMIN,
    )


@pytest.fixture()
def test_user_dict_moderator():
    return dict(
        email="test_moderator_email@mail.ru",
        username="moderatormoderator",
        phone_number="5475475",
        name="Example",
        surname="Example",
        password="1234567Psg",
        group_id=None,
        group_name="test 3",
        role=Role.MODERATOR,
    )


@pytest_asyncio.fixture(scope="function")
async def create_user_and_login_success(
    test_client: AsyncClient, test_user_sign_up_dict, refresh_tables
) -> Response:
    signup_data = SignUpModel(**test_user_sign_up_dict)
    login_data = CredentialsModel(
        login=test_user_sign_up_dict.get("username"),
        password=test_user_sign_up_dict.get("password"),
    )

    await test_client.post("/v1/auth/signup", data=signup_data.__dict__)
    return await test_client.post("/v1/auth/login", json=login_data.model_dump())


async def create_user(
    user_model_dict: dict, group_name: str, get_test_async_session: AsyncSession
):
    group = await SQLAlchemyGroupRepository(get_test_async_session).create_group(
        group_name=group_name
    )
    return await SQLAlchemyUserRepository(get_test_async_session).create_user(
        UserCreateModel(
            email=user_model_dict.get("email"),
            username=user_model_dict.get("username"),
            phone_number=user_model_dict.get("phone_number"),
            group_id=group.id,
            password="testHashedPassword",
            role=user_model_dict.get("role"),
        )
    )


@pytest_asyncio.fixture(scope="function")
async def user_with_role_user(test_user_dict_user, get_test_async_session):
    user = await create_user(test_user_dict_user, "test", get_test_async_session)
    yield user
    await SQLAlchemyUserRepository(get_test_async_session).delete_user(user_id=user.id)


@pytest_asyncio.fixture(scope="function")
async def user_with_role_admin(test_user_dict_admin, get_test_async_session):
    user = await create_user(test_user_dict_admin, "test", get_test_async_session)
    yield user
    await SQLAlchemyUserRepository(get_test_async_session).delete_user(user_id=user.id)


@pytest_asyncio.fixture(scope="function")
async def user_with_role_moderator(test_user_dict_moderator, get_test_async_session):
    user = await create_user(test_user_dict_moderator, "test", get_test_async_session)
    yield user
    await SQLAlchemyUserRepository(get_test_async_session).delete_user(user_id=user.id)


@pytest_asyncio.fixture(scope="function")
async def moderator_and_user_with_different_groups(
    test_user_dict_moderator, test_user_dict_user, get_test_async_session
):
    user_moderator = await create_user(
        test_user_dict_moderator, "abc1", get_test_async_session
    )
    user = await create_user(test_user_dict_user, "abc2", get_test_async_session)
    yield {"user_with_role_moderator": user_moderator, "user_with_differ_role": user}
    await SQLAlchemyUserRepository(get_test_async_session).delete_user(
        user_id=user_moderator.id
    )
    await SQLAlchemyUserRepository(get_test_async_session).delete_user(user_id=user.id)


def jwt_access_token(user: UserResponseModel):
    return generate_token(
        payload=TokenDataWithTokenType(
            token_type=TokenType.ACCESS,
            user_id=str(user.id),
            role=user.role,
            group_id=str(user.group_id),
            is_blocked=user.is_blocked,
        ),
        expires_delta=timedelta(minutes=5),
    )
