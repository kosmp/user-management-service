from datetime import timedelta

import pytest
from httpx import AsyncClient

from src.ports.enums import TokenType
from src.core.services.token import generate_token
from src.ports.schemas.user import (
    SignUpModel,
    CredentialsModel,
    TokenDataWithTokenType,
)
from tests.integration.conftest import serialize, create_user
from src.adapters.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


@pytest.mark.asyncio
async def test_auth_signup(test_client: AsyncClient, test_user_sign_up_dict):
    signup_data = SignUpModel(**test_user_sign_up_dict)

    response = await test_client.post("/v1/auth/signup", data=signup_data.__dict__)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_signup_email_exists(
    test_client: AsyncClient, test_user_sign_up_dict_2, test_user_sign_up_dict_3
):
    signup_data_1 = SignUpModel(**test_user_sign_up_dict_2)
    signup_data_2 = SignUpModel(**test_user_sign_up_dict_3)

    await test_client.post("/v1/auth/signup", data=signup_data_1.__dict__)
    response = await test_client.post("/v1/auth/signup", data=signup_data_2.__dict__)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_signup_email_exists(
    test_client: AsyncClient, test_user_sign_up_dict
):
    signup_data_1 = SignUpModel(**test_user_sign_up_dict)
    signup_data_2 = SignUpModel(**test_user_sign_up_dict)

    await test_client.post("/v1/auth/signup", data=signup_data_1.__dict__)
    response = await test_client.post("/v1/auth/signup", data=signup_data_2.__dict__)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_login_success(
    test_client: AsyncClient, create_user_and_login_success
):
    response = create_user_and_login_success

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_login_with_wrong_pass(
    test_client: AsyncClient, test_user_sign_up_dict
):
    signup_data = SignUpModel(**test_user_sign_up_dict)
    password = test_user_sign_up_dict.get("password") + "123"
    login_data = CredentialsModel(
        login=test_user_sign_up_dict.get("username"), password=password
    )

    await test_client.post("/v1/auth/signup", data=signup_data.__dict__)
    response = await test_client.post("/v1/auth/login", json=login_data.model_dump())

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_login_with_invalid_login(
    test_client: AsyncClient, test_user_sign_up_dict
):
    signup_data = SignUpModel(**test_user_sign_up_dict)
    login = "ab" + test_user_sign_up_dict.get("username")
    login_data = CredentialsModel(
        login=login, password=test_user_sign_up_dict.get("password")
    )

    await test_client.post("/v1/auth/signup", data=signup_data.__dict__)
    response = await test_client.post("/v1/auth/login", json=login_data.model_dump())

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_auth_refresh_token_endpoint(
    test_client: AsyncClient, create_user_and_login_success
):
    response_login = create_user_and_login_success

    refresh_token: str or None = None
    if response_login.status_code == 200:
        refresh_token = serialize(response_login.content).get("refresh_token")

    response_refresh = await test_client.post(
        "/v1/auth/refresh-token", params={"token": refresh_token}
    )

    assert response_refresh.status_code == 200


@pytest.mark.asyncio
async def test_auth_refresh_endpoint_using_access_token(
    test_client: AsyncClient, create_user_and_login_success
):
    response_login = create_user_and_login_success

    access_token: str or None = None

    if response_login.status_code == 200:
        access_token = serialize(response_login.content).get("access_token")

    response_refresh = await test_client.post(
        "/v1/auth/refresh-token", params={"token": access_token}
    )

    assert response_refresh.status_code == 401


@pytest.mark.asyncio
async def test_auth_request_reset_password_success(
    test_client: AsyncClient, test_user_sign_up_dict, create_user_and_login_success
):
    email = test_user_sign_up_dict.get("email")

    response = await test_client.post(
        "/v1/auth/request-password-reset", params={"email": email}
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_request_reset_password_with_not_existed_email(
    test_client: AsyncClient, test_user_sign_up_dict, create_user_and_login_success
):
    email = test_user_sign_up_dict.get("email")

    response = await test_client.post(
        "/v1/auth/request-password-reset", params={"email": email}
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_request_reset_password_with_not_existed_email(
    test_client: AsyncClient, test_user_dict_user, create_user_and_login_success
):
    email = "ab" + test_user_dict_user.get("email")

    response = await test_client.post(
        "/v1/auth/request-password-reset", params={"email": email}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_auth_reset_password(
    test_client: AsyncClient, get_test_async_session, test_user_dict_user
):
    user = await create_user(test_user_dict_user, "test", get_test_async_session)

    test_refresh_token = generate_token(
        payload=TokenDataWithTokenType(
            token_type=TokenType.REFRESH,
            user_id=str(user.id),
            role=user.role,
            group_id=str(user.group_id),
            is_blocked=user.is_blocked,
        ),
        expires_delta=timedelta(minutes=5),
    )

    response = await test_client.put(
        "/v1/auth/reset-password",
        params={"token": test_refresh_token},
        json={"password": "1234567Psg"},
    )

    user = await SQLAlchemyUserRepository(get_test_async_session).get_user(
        user_id=user.id
    )

    assert response.status_code == 200 and user.password != test_user_dict_user.get(
        "password"
    )
