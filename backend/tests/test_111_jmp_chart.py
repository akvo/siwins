import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session

pytestmark = pytest.mark.asyncio
sys.path.append("..")


class TestJMPChartEndpoint:
    @pytest.mark.asyncio
    async def test_get_bar_charts_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation")
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            "question": "Sanitation",
            "data": [
                {
                    "administration": "Malaita",
                    "score": 0,
                    "child": []},
                {
                    "administration": "Rennell and Bellona",
                    "score": 0,
                    "child": []},
                {
                    "administration": "Temotu",
                    "score": 0,
                    "child": []},
                {
                    "administration": "Western",
                    "score": 0,
                    "child": []},
                {
                    "administration": "Choiseul",
                    "score": 0,
                    "child": []},
                {
                    "administration": "Guadalcanal",
                    "score": 0,
                    "child": [
                        {
                            "option": "No Service",
                            "count": 1,
                            "percent": 100.0,
                            "color": None
                        }
                    ],
                },
                {
                    "administration": "Honiara",
                    "score": 0,
                    "child": []},
                {
                    "administration": "Isabel",
                    "score": 0,
                    "child": []},
                {
                    "administration": "Makira and Ulawa",
                    "score": 0,
                    "child": []},
                {
                    "administration": "Central",
                    "score": 0,
                    "child": []},
            ],
        }
