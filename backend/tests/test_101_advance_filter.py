import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestQuestionRoutes:
    @pytest.mark.asyncio
    async def test_get_question_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("question:get_all_question")
        )
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            "id": 654960929,
            "name": "Which year was the survey conducted?",
            "type": "option",
            "option": [{
                'code': None,
                'id': 1,
                'name': '2018',
                'order': 1
            }, {
                'code': None,
                'id': 2,
                'name': '2023',
                'order': 2
            }],
            "attributes": [],
            "number": []
        }
        # filter by question attribute
        res = await client.get(
            app.url_path_for("question:get_all_question"),
            params={"attribute": "indicator"}
        )
        assert res.status_code == 200
        res = res.json()
        name = 'Is drinking water from the main source '
        name += 'typically available throughout the school year?'
        assert res[1] == {
            'id': 624660927,
            'name': name,
            "type": "option",
            'attributes': ['indicator', 'advance_filter'],
            'option': [{
                'id': 47,
                'name': 'Yes (always available)',
                'order': 1,
                'code': 'W5a'
            }, {
                'id': 48,
                'name': 'Mostly (unavailable ≤ 30 days total)',
                'order': 2,
                'code': 'W5b'
            }, {
                'id': 49,
                'name': 'No (unavailable > 30 days total)',
                'order': 3,
                'code': 'W5c'
            }, {
                'id': 50,
                'name': "Don't know/can't say",
                'order': 4,
                'code': 'W5d'
            }],
            'number': []
        }
        for r in res:
            if r['type'] != 'number' or not r['number']:
                continue
            assert r['type'] == 'number'
            for x in r['number']:
                assert 'value' in x
                assert 'count' in x
