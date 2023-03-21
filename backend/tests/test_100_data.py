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
    async def test_get_paginated_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("data:get_all"))
        assert res.status_code == 200
        res = res.json()
        assert res == {
            "current": 1,
            "data": [{
                "id": 642650980,
                "name": "SMA Negeri 1 Nusa Penida - High school",
                "form": 733030972,
                "registration": True,
                "datapoint_id": 716330915,
                "identifier": "dfmn-hw5g-11se",
                "geo": {
                    "long": 115.49182166666667,
                    "lat": -8.676368333333333
                },
                "created": "December 01, 2022",
                "updated": "December 01, 2022",
                "answer": [{
                    "question": 718001069,
                    "value": "High school"
                }, {
                    "question": 721880978,
                    "value": "-8.676368333333333|115.49182166666667",
                }, {
                    "question": 738940972,
                    "value": "SMA Negeri 1 Nusa Penida"
                }],
            }],
            "total": 1,
            "total_page": 1,
        }

    @pytest.mark.asyncio
    async def test_get_data_detail(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("data:get_data_detail", data_id=642650980))
        assert res.status_code == 200
        res = res.json()
        assert res == {
            "id": 642650980,
            "name": "SMA Negeri 1 Nusa Penida - High school",
            "geo": {
                "long": 115.49182166666667,
                "lat": -8.676368333333333
            },
            "answer": [{
                "question_id": 718001069,
                "value": "High school",
                "history": False,
            }, {
                "question_id": 721880978,
                "value": "-8.676368333333333|115.49182166666667",
                "history": False,
            }, {
                "question_id": 738940972,
                "value": "SMA Negeri 1 Nusa Penida",
                "history": False,
            }],
        }

    @pytest.mark.asyncio
    async def test_get_maps_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # without indicator
        res = await client.get(app.url_path_for("data:get_maps_data"))
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 632510922,
            'identifier': 'd5bi-mkoi-qrej',
            'geo': [-47.72084919070232, 71.64445931032847],
            'name': 'Untitled',
            'answer': {}
        }
        # with indicator
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 624660930})
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 632510922,
            'identifier': 'd5bi-mkoi-qrej',
            'geo': [-47.72084919070232, 71.64445931032847],
            'name': 'Untitled',
            'answer': {
                'question': 624660930,
                'value': 'No'
            }
        }
        # with indicator & indicator option filter
        # option indicator with number filter
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 624660930, "number": [10, 20]})
        assert res.status_code == 400
        # option indicator with option filter
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 624660930, "q": "624660930|no"})
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 632510922,
            'identifier': 'd5bi-mkoi-qrej',
            'geo': [-47.72084919070232, 71.64445931032847],
            'name': 'Untitled',
            'answer': {
                'question': 624660930,
                'value': 'No'
            }
        }
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 624660930, "q": "624660930|yes"})
        assert res.status_code == 200
        res = res.json()
        assert res == []
        # number indicator with number filter
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 630020919})
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 632510922,
            'identifier': 'd5bi-mkoi-qrej',
            'geo': [-47.72084919070232, 71.64445931032847],
            'name': 'Untitled',
            'answer': {
                'question': 630020919,
                'value': 12
            }
        }
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 630020919, "number": [11]})
        assert res.status_code == 400
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 630020919, "number": [1, 10]})
        assert res.status_code == 200
        res = res.json()
        assert res == []
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 630020919, "number": [1, 20]})
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 632510922,
            'identifier': 'd5bi-mkoi-qrej',
            'geo': [-47.72084919070232, 71.64445931032847],
            'name': 'Untitled',
            'answer': {
                'question': 630020919,
                'value': 12
            }
        }

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
