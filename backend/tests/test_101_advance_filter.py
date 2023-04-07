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
            "option": [{
                'code': None,
                'id': 1,
                'name': '2018',
                'order': None
            }, {
                'code': None,
                'id': 2,
                'name': '2023',
                'order': None
            }],
            "attributes": []
        }
        # filter by question attribute
        res = await client.get(
            app.url_path_for("question:get_all_question"),
            params={"attribute": "indicator"}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == []
