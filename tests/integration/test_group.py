import pytest
from httpx import AsyncClient

from tests.integration.conftest import jwt_token


@pytest.mark.asyncio
async def test_group_create_by_user(client: AsyncClient, user_with_role_user):
    response = await client.post(
        f"/v1/group",
        data={"name": "testadfdg"},
        headers={"Authorization": f"Bearer {jwt_token(user_with_role_user)}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_group_create_by_admin(client: AsyncClient, user_with_role_admin):
    response = await client.post(
        f"/v1/group",
        params={"group_name": "testad"},
        headers={"Authorization": f"Bearer {jwt_token(user_with_role_admin)}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_group_by_user(client: AsyncClient, user_with_role_user):
    response = await client.get(
        f"/v1/group/{user_with_role_user.group_id}",
        headers={"Authorization": f"Bearer {jwt_token(user_with_role_user)}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_group_by_user(client: AsyncClient, user_with_role_user):
    response = await client.delete(
        f"/v1/group/{user_with_role_user.group_id}",
        headers={"Authorization": f"Bearer {jwt_token(user_with_role_user)}"},
    )

    assert response.status_code == 403
