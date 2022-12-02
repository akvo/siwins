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
        assert res == [{
            "id": 1,
            "name": "SMA N 1 Nusa Penida - High school",
            "geo": {"long": 115.49182166666667, "lat": -8.676368333333333},
        }, {
            "id": 2,
            "name": "SMK N 1 Nusa Penida - High school",
            "geo": {"long": 115.49200166666667, "lat": -8.676591666666667},
        }]
