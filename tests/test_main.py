import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_webhook():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {"nome_tutor": "Carla", "telefone": "35999998888", "nome_cao": "Thor"}
        response = await ac.post("/webhook/inlead", data=data)
        assert response.status_code in (200, 502)
