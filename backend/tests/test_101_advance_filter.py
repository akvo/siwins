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
            "id": 738940972,
            "name": "Example School Name",
            "option": [],
            "attributes": []
        }
        # filter by question attribute
        res = await client.get(
            app.url_path_for("question:get_all_question"),
            params={"attribute": "indicator"}
        )
        assert res.status_code == 200
        res = res.json()
        assert res[0] == {
            "id": 718001069,
            "name": "Type of school",
            "attributes": ["advance_filter", "indicator"],
            "option": [{
                "id": 1,
                "name": "Junior school",
                "code": None,
                "order": None
            }, {
                "id": 2,
                "name": "Primary school",
                "code": None,
                "order": None
            }, {
                "id": 3,
                "name": "High school",
                "code": None,
                "order": None
            }],
        }
