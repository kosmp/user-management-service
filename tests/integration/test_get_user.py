import pytest
from httpx import AsyncClient
from tests.integration.conftest import jwt_access_token


@pytest.mark.asyncio
async def test_get_user_with_role_user(test_client: AsyncClient, user_with_role_user):
    response = await test_client.get(
        f"/v1/user/{user_with_role_user.id}",
        headers={"Authorization": f"Bearer {jwt_access_token(user_with_role_user)}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_with_role_admin(test_client: AsyncClient, user_with_role_admin):
    response = await test_client.get(
        f"/v1/user/{user_with_role_admin.id}",
        headers={"Authorization": f"Bearer {jwt_access_token(user_with_role_admin)}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user_with_role_moderator_and_same_group(
    test_client: AsyncClient, user_with_role_moderator
):
    response = await test_client.get(
        f"/v1/user/{user_with_role_moderator.id}",
        headers={
            "Authorization": f"Bearer {jwt_access_token(user_with_role_moderator)}"
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user_with_role_moderator_and_different_group(
    test_client: AsyncClient, moderator_and_user_with_different_groups
):
    user_with_differ_role = moderator_and_user_with_different_groups.get(
        "user_with_differ_role"
    )
    moderator = moderator_and_user_with_different_groups.get("user_with_role_moderator")
    response = await test_client.get(
        f"/v1/user/{user_with_differ_role.id}",
        headers={"Authorization": f"Bearer {jwt_access_token(moderator)}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me(test_client: AsyncClient, user_with_role_user):
    response = await test_client.get(
        f"/v1/user/me",
        headers={"Authorization": f"Bearer {jwt_access_token(user_with_role_user)}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_users_for_admin(test_client: AsyncClient, user_with_role_admin):
    response = await test_client.get(
        f"/v1/users",
        headers={"Authorization": f"Bearer {jwt_access_token(user_with_role_admin)}"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_users_for_user_role(test_client: AsyncClient, user_with_role_user):
    response = await test_client.get(
        f"/v1/users",
        headers={"Authorization": f"Bearer {jwt_access_token(user_with_role_user)}"},
    )

    assert response.status_code == 403
