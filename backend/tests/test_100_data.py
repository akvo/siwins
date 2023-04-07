import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from db import crud_data

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestDataRoutes:
    @pytest.mark.asyncio
    async def test_get_maps_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # without indicator
        res = await client.get(app.url_path_for("data:get_maps_data"))
        assert res.status_code == 200
        res = res.json()
        assert res == []
        # with indicator
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 738950915})
        assert res.status_code == 200
        res = res.json()
        assert res == []

    @pytest.mark.asyncio
    async def test_get_chart_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # get chart data without query params
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980)
        )
        assert res.status_code == 404
        # get chart data with history param True
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"history": True},
        )
        assert res.status_code == 404
        # get chart data with question_ids param
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"question_ids": [735090984]},
        )
        assert res.status_code == 404
        # get chart data with question_ids and history param
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"question_ids": [735090984], "history": True},
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_get_last_history_empty(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        fd = crud_data.get_last_history(
            session=session, datapoint_id=642770963, id=754830913
        )
        assert fd == []
