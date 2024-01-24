import pytest
from httpx import AsyncClient, Response
from src.ports.schemas.user import SignUpModel, CredentialsModel
from conftest import serialize


@pytest.mark.asyncio
async def test_auth_signup(test_client: AsyncClient, test_user_dict_1, refresh_tables):
    signup_data = SignUpModel(**test_user_dict_1)

    response = await test_client.post("/v1/auth/signup", data=signup_data.__dict__)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_signup_email_exists(
    test_client: AsyncClient, test_user_dict_2, test_user_dict_3, refresh_tables
):
    signup_data_1 = SignUpModel(**test_user_dict_2)
    signup_data_2 = SignUpModel(**test_user_dict_3)

    await test_client.post("/v1/auth/signup", data=signup_data_1.__dict__)
    response = await test_client.post("/v1/auth/signup", data=signup_data_2.__dict__)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_signup_email_exists(
    test_client: AsyncClient, test_user_dict_1, refresh_tables
):
    signup_data_1 = SignUpModel(**test_user_dict_1)
    signup_data_2 = SignUpModel(**test_user_dict_1)

    await test_client.post("/v1/auth/signup", data=signup_data_1.__dict__)
    response = await test_client.post("/v1/auth/signup", data=signup_data_2.__dict__)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_login_success(
    test_client: AsyncClient, test_user_dict_4, login_success
):
    response = login_success

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_login_with_wrong_pass(
    test_client: AsyncClient, test_user_dict_4, refresh_tables
):
    signup_data = SignUpModel(**test_user_dict_4)
    password = test_user_dict_4.get("password") + "123"
    login_data = CredentialsModel(
        login=test_user_dict_4.get("username"), password=password
    )

    await test_client.post("/v1/auth/signup", data=signup_data.__dict__)
    response = await test_client.post("/v1/auth/login", json=login_data.model_dump())

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_login_with_invalid_login(
    test_client: AsyncClient, test_user_dict_4, refresh_tables
):
    signup_data = SignUpModel(**test_user_dict_4)
    login = "ab" + test_user_dict_4.get("username")
    login_data = CredentialsModel(
        login=login, password=test_user_dict_4.get("password")
    )

    await test_client.post("/v1/auth/signup", data=signup_data.__dict__)
    response = await test_client.post("/v1/auth/login", json=login_data.model_dump())

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_auth_refresh_token_endpoint(test_client: AsyncClient, login_success):
    response_login = login_success

    refresh_token: str or None = None
    if response_login.status_code == 200:
        refresh_token = serialize(response_login.content).get("refresh_token")

    response_refresh = await test_client.post(
        "/v1/auth/refresh-token", params={"token": refresh_token}
    )

    assert response_refresh.status_code == 200


@pytest.mark.asyncio
async def test_auth_refresh_endpoint_using_access_token(
    test_client: AsyncClient, login_success
):
    response_login = login_success

    access_token: str or None = None

    if response_login.status_code == 200:
        access_token = serialize(response_login.content).get("access_token")

    response_refresh = await test_client.post(
        "/v1/auth/refresh-token", params={"token": access_token}
    )

    assert response_refresh.status_code == 401
