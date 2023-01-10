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
            app.url_path_for("question:question_route_for_advance_filter")
        )
        assert res.status_code == 200
        res = res.json()
        assert res == [
            {
                "id": 718001069,
                "name": "Type of school",
                "option": [
                    {
                        "id": 1,
                        "name": "Junior school",
                        "order": None,
                        "code": None,
                    },
                    {
                        "id": 2,
                        "name": "Primary school",
                        "order": None,
                        "code": None,
                    },
                    {
                        "id": 3,
                        "name": "High school",
                        "order": None,
                        "code": None,
                    },
                ],
            },
            {
                "id": 738950915,
                "name": "Status of toilet",
                "option": [
                    {"id": 4, "name": "Dirty", "order": None, "code": None},
                    {"id": 5, "name": "Clean", "order": None, "code": None},
                    {
                        "id": 6,
                        "name": "No toilets",
                        "order": None,
                        "code": None,
                    },
                ],
            },
        ]
