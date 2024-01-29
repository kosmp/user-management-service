import pytest
from httpx import AsyncClient
from tests.integration.conftest import jwt_token, serialize


@pytest.mark.asyncio
async def test_delete_me(client: AsyncClient, user_with_role_user):
    response = await client.delete(
        f"/v1/user/me",
        headers={"Authorization": f"Bearer {jwt_token(user_with_role_user)}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_me(client: AsyncClient, user_with_role_user):
    new_surname = user_with_role_user.surname + "ab"
    response = await client.patch(
        f"/v1/user/me",
        data={"surname": new_surname},
        headers={"Authorization": f"Bearer {jwt_token(user_with_role_user)}"},
    )

    surname = serialize(response.content).get("surname")

    assert surname != user_with_role_user.surname


@pytest.mark.asyncio
async def test_update_user_by_admin(client: AsyncClient, user_with_role_admin):
    new_surname = user_with_role_admin.surname + "ab"
    response = await client.patch(
        f"/v1/user/{user_with_role_admin.id}/update",
        data={"surname": new_surname},
        headers={"Authorization": f"Bearer {jwt_token(user_with_role_admin)}"},
    )

    surname = serialize(response.content).get("surname")

    assert surname != user_with_role_admin.surname


@pytest.mark.asyncio
async def test_update_user_by_user(client: AsyncClient, user_with_role_user):
    response = await client.patch(
        f"/v1/user/{user_with_role_user.id}/update",
        data={"surname": user_with_role_user.surname},
        headers={"Authorization": f"Bearer {jwt_token(user_with_role_user)}"},
    )

    assert response.status_code == 403
