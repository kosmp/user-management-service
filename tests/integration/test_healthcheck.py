import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_healthcheck(test_client: AsyncClient):
    response = await test_client.get("/healthcheck")

    assert response.status_code == 200
