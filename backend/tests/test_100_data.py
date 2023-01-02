import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestDataRoutes:
    @pytest.mark.asyncio
    async def test_get_maps_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("data:get_maps_data"))
        assert res.status_code == 200
        res = res.json()
        assert res == [
            {
                "id": 642650980,
                "name": "SMA N 1 Nusa Penida - High school",
                "geo": [-8.676368333333333, 115.49182166666667],
            }
        ]

    @pytest.mark.asyncio
    async def test_get_chart_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # get chart data without query params
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980)
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            "id": 642650980,
            "name": "SMA N 1 Nusa Penida - High school",
            "monitoring": [
                {
                    "question_id": 725310914,
                    "question": "Number students",
                    "type": "number",
                    "value": 100,
                    "date": "Dec 02, 2022 - 3:03:25 AM",
                    "history": False,
                },
                {
                    "question_id": 735090984,
                    "question": "Number toilets",
                    "type": "number",
                    "value": 10,
                    "date": "Dec 02, 2022 - 3:03:25 AM",
                    "history": False,
                },
                {
                    "question_id": 738950915,
                    "question": "Status of toilet",
                    "type": "option",
                    "value": "Clean",
                    "date": "Dec 02, 2022 - 3:03:25 AM",
                    "history": False,
                },
            ],
        }
        # get chart data with history param True
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"history": True},
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            "id": 642650980,
            "name": "SMA N 1 Nusa Penida - High school",
            "monitoring": [
                {
                    "question_id": 725310914,
                    "question": "Number students",
                    "type": "number",
                    "value": 100,
                    "date": "Dec 02, 2022 - 3:03:25 AM",
                    "history": False,
                },
                {
                    "question_id": 735090984,
                    "question": "Number toilets",
                    "type": "number",
                    "value": 10,
                    "date": "Dec 02, 2022 - 3:03:25 AM",
                    "history": False,
                },
                {
                    "question_id": 738950915,
                    "question": "Status of toilet",
                    "type": "option",
                    "value": "Clean",
                    "date": "Dec 02, 2022 - 3:03:25 AM",
                    "history": False,
                },
                {
                    "question_id": 725310914,
                    "question": "Number students",
                    "type": "number",
                    "value": 110,
                    "date": "Dec 02, 2022 - 3:02:59 AM",
                    "history": True,
                },
                {
                    "question_id": 735090984,
                    "question": "Number toilets",
                    "type": "number",
                    "value": 11,
                    "date": "Dec 02, 2022 - 3:02:59 AM",
                    "history": True,
                },
                {
                    "question_id": 738950915,
                    "question": "Status of toilet",
                    "type": "option",
                    "value": "Clean",
                    "date": "Dec 02, 2022 - 3:02:59 AM",
                    "history": True,
                },
            ],
        }
        # get chart data with question_ids param
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"question_ids": [735090984]},
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            "id": 642650980,
            "name": "SMA N 1 Nusa Penida - High school",
            "monitoring": [
                {
                    "question_id": 735090984,
                    "question": "Number toilets",
                    "type": "number",
                    "value": 10,
                    "date": "Dec 02, 2022 - 3:03:25 AM",
                    "history": False,
                }
            ],
        }
        # get chart data with question_ids and history param
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"question_ids": [735090984], "history": True},
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            "id": 642650980,
            "name": "SMA N 1 Nusa Penida - High school",
            "monitoring": [
                {
                    "question_id": 735090984,
                    "question": "Number toilets",
                    "type": "number",
                    "value": 10,
                    "date": "Dec 02, 2022 - 3:03:25 AM",
                    "history": False,
                },
                {
                    "question_id": 735090984,
                    "question": "Number toilets",
                    "type": "number",
                    "value": 11,
                    "date": "Dec 02, 2022 - 3:02:59 AM",
                    "history": True,
                },
            ],
        }
