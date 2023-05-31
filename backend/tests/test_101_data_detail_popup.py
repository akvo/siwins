import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from tests.test_school_detail_popup_dump import (
    res_school_detail_popup
)

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestDataDetailRoutes:
    @pytest.mark.asyncio
    async def test_get_data_detail(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("data:get_data_detail", data_id=649130936))
        assert res.status_code == 200
        res = res.json()
        assert res == res_school_detail_popup

    @pytest.mark.asyncio
    async def test_get_answer_history(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # no datapoint
        res = await client.get(
            app.url_path_for("answer:get_history", data_id=12345),
            params={'question_id': 640620926})
        assert res.status_code == 404
        # no question
        res = await client.get(
            app.url_path_for("answer:get_history", data_id=649130936),
            params={'question_id': 12345})
        assert res.status_code == 404
        # option question
        res = await client.get(
            app.url_path_for("answer:get_history", data_id=649130936),
            params={'question_id': 640620926})
        assert res.status_code == 404
        # correct data
        res = await client.get(
            app.url_path_for("answer:get_history", data_id=649130936),
            params={'question_id': 624670928})
        assert res.status_code == 200
        res = res.json()
        assert res == [{
            'question_id': 624670928,
            'question_name': 'No. of classrooms',
            'type': 'number',
            'history': True,
            'year': 2018,
            'value': [{
                'level': 'AO CHS - 21710',
                'total': 12.0,
                'count': 1,
                'value': 12.0,
            }, {
                'level': 'Guadalcanal',
                'total': 12.0,
                'count': 1,
                'value': 12.0,
            }, {
                'level': 'National',
                'total': 12.0,
                'count': 1,
                'value': 12.0,
            }],
            'render': 'chart'
        }]
