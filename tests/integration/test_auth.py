import pytest
from httpx import AsyncClient
from src.ports.schemas.user import SignUpModel


@pytest.mark.asyncio
async def test_auth_signup(test_client: AsyncClient, test_user_dict_1):
    signup_data = SignUpModel(**test_user_dict_1)

    response = await test_client.post("/v1/auth/signup", data=signup_data.__dict__)

    assert response.status_code == 200
