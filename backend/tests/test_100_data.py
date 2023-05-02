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
        assert "current" in res
        assert "data" in res
        assert "total" in res
        assert "total_page" in res

    @pytest.mark.asyncio
    async def test_get_maps_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # without indicator
        res = await client.get(app.url_path_for("data:get_maps_data"))
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 649130936,
            'identifier': 'eptc-hraw-kkps',
            'geo': [-51.14834033402119, 41.7559732176761],
            'school_information': [
                'Guadalcanal', 'Community High School', 'AO CHS', '21710'],
            'name': 'Untitled',
            'year_conducted': 2023,
            'answer': {}
        }
        # with indicator
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 624660930})
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 649130936,
            'identifier': 'eptc-hraw-kkps',
            'geo': [-51.14834033402119, 41.7559732176761],
            'school_information': [
                'Guadalcanal', 'Community High School', 'AO CHS', '21710'],
            'name': 'Untitled',
            'year_conducted': 2023,
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
        assert res == []
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
            'id': 649130936,
            'identifier': 'eptc-hraw-kkps',
            'geo': [-51.14834033402119, 41.7559732176761],
            'school_information': [
                'Guadalcanal', 'Community High School', 'AO CHS', '21710'],
            'name': 'Untitled',
            'year_conducted': 2023,
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
            'id': 649130936,
            'identifier': 'eptc-hraw-kkps',
            'geo': [-51.14834033402119, 41.7559732176761],
            'school_information': [
                'Guadalcanal', 'Community High School', 'AO CHS', '21710'],
            'name': 'Untitled',
            'year_conducted': 2023,
            'answer': {
                'question': 630020919,
                'value': 12
            }
        }
        # filter by province
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 630020919, "prov": ["Central"]})
        assert res.status_code == 200
        res = res.json()
        assert res == []
        # filter by province
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 630020919, "prov": ["Guadalcanal"]})
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 649130936,
            'identifier': 'eptc-hraw-kkps',
            'geo': [-51.14834033402119, 41.7559732176761],
            'school_information': [
                'Guadalcanal', 'Community High School', 'AO CHS', '21710'],
            'name': 'Untitled',
            'year_conducted': 2023,
            'answer': {
                'question': 630020919,
                'value': 12
            }
        }
        # filter by school type
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={
                "indicator": 630020919,
                "sctype": ["Primary School"]
            })
        assert res.status_code == 200
        res = res.json()
        assert res == []
        # filter by school type
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={
                "indicator": 630020919,
                "sctype": ["Community High School"]
            })
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 649130936,
            'identifier': 'eptc-hraw-kkps',
            'geo': [-51.14834033402119, 41.7559732176761],
            'school_information': [
                'Guadalcanal', 'Community High School', 'AO CHS', '21710'],
            'name': 'Untitled',
            'year_conducted': 2023,
            'answer': {
                'question': 630020919,
                'value': 12
            }
        }
        # filter by school type and province
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={
                "indicator": 630020919,
                "prov": ["Central"],
                "sctype": ["Community High School"]
            })
        assert res.status_code == 200
        res = res.json()
        assert res == []
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={
                "indicator": 630020919,
                "prov": ["Guadalcanal"],
                "sctype": ["Community High School"]
            })
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            'id': 649130936,
            'identifier': 'eptc-hraw-kkps',
            'geo': [-51.14834033402119, 41.7559732176761],
            'school_information': [
                'Guadalcanal', 'Community High School', 'AO CHS', '21710'],
            'name': 'Untitled',
            'year_conducted': 2023,
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
