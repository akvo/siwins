import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestOptionRoutes:
    @pytest.mark.asyncio
    async def test_get_option_monitoring_round(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("option:get_monitoring_round")
        )
        assert res.status_code == 200
        res = res.json()
        assert res == [2018, 2023, 2024, 2025, 2026]
