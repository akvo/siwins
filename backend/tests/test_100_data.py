import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestDataRoutes():
    @pytest.mark.asyncio
    async def test_get_maps_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("data:get_maps_data"))
        assert res.status_code == 200
        res = res.json()
        for r in res:
            assert "id" in r
            assert "name" in r
            assert "geo" in r

    @pytest.mark.asyncio
    async def test_get_chart_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=1))
        assert res.status_code == 200
        res = res.json()
        assert "id" in res
        assert "name" in res
        assert "monitoring" in res
        for m in res.get('monitoring'):
            assert "question_id" in m
            assert "question" in m
            assert "value" in m
            assert "value" in m
            assert "history" in m
