import sys
import pytest
from os.path import exists
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from AkvoResponseGrouper.cli.generate_schema import generate_schema
from AkvoResponseGrouper.views import (
    get_categories,
    refresh_view,
)

pytestmark = pytest.mark.asyncio
sys.path.append("..")


class TestMigrationCategory:
    @pytest.mark.asyncio
    async def test_if_views_is_successfully_added(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        schema = generate_schema(file_config="./source/category.json")
        session.execute(text(schema))
        # check if .category.json was created
        assert exists("./.category.json") is True
        # REFRESH VIEW
        refresh_view(session=session)
        res = get_categories(session=session)
        assert len(res) > 1

    @pytest.mark.asyncio
    async def test_get_bar_charts_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        res = await client.get(
            app.url_path_for("charts:get_bar_charts"),
        )
        assert res.status_code == 200

        res = res.json()
        assert res == [
            {
                "category": "Hygiene",
                "form": 647170919,
                "options": [
                    {"name": "Basic", "count": 1},
                ],
            },
            {
                "category": "Sanitation",
                "form": 647170919,
                "options": [
                    {"name": "No Service", "count": 1},
                ],
            },
            {
                "category": "Water",
                "form": 647170919,
                "options": [
                    {"name": "Safely Managed", "count": 1},
                ],
            },
        ]

    @pytest.mark.asyncio
    async def test_get_bar_charts_filter_by_name_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        api_url = app.url_path_for("charts:get_bar_charts")
        res = await client.get(f"{api_url}?name=Water")
        assert res.status_code == 200

        res = res.json()
        assert res == [
            {
                "category": "Water",
                "form": 647170919,
                "options": [
                    {"name": "Safely Managed", "count": 1},
                ],
            },
        ]
