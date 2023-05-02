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


class TestMigrationCategoryAndNationalData:
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
    async def test_get_number_of_school(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        res = await client.get(
            app.url_path_for("charts:get_number_of_school"),
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            "name": "Number of schools",
            "total": 1
        }

    @pytest.mark.asyncio
    async def test_get_bar_charts_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        res = await client.get(
            app.url_path_for("charts:get_bar_charts"),
        )
        assert res.status_code == 200
        res = res.json()
        assert res == [{
            'category': 'Hygiene',
            'form': 647170919,
            'options': [{
                'name': 'Basic',
                'color': '#51B453',
                'count': 1
            }, {
                'name': 'Limited',
                'color': '#fff176',
                'count': 0
            }, {
                'name': 'No Service',
                'color': '#FEBC11',
                'count': 0
            }]
        }, {
            'category': 'Sanitation',
            'form': 647170919,
            'options': [{
                'name': 'Basic',
                'color': '#ab47bc',
                'count': 0
            }, {
                'name': 'Limited',
                'color': '#fff176',
                'count': 1
            }, {
                'name': 'No Service',
                'color': '#FEBC11',
                'count': 0
            }]
        }, {
            'category': 'Water',
            'form': 647170919,
            'options': [{
                'name': 'Safely Managed',
                'color': '#0080c6',
                'count': 0
            }, {
                'name': 'Basic',
                'color': '#00b8ec',
                'count': 0
            }, {
                'name': 'Limited',
                'color': '#fff176',
                'count': 1
            }, {
                'name': 'No Service',
                'color': '#FEBC11',
                'count': 0
            }]
        }]

    @pytest.mark.asyncio
    async def test_get_bar_charts_filter_by_name_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        api_url = app.url_path_for("charts:get_bar_charts")
        res = await client.get(f"{api_url}?name=Water")
        assert res.status_code == 200
        res = res.json()
        assert res == [{
            'category': 'Water',
            'form': 647170919,
            'options': [{
                'name': 'Safely Managed',
                'color': '#0080c6',
                'count': 0
            }, {
                'name': 'Basic',
                'color': '#00b8ec',
                'count': 0
            }, {
                'name': 'Limited',
                'color': '#fff176',
                'count': 1
            }, {
                'name': 'No Service',
                'color': '#FEBC11',
                'count': 0
            }]
        }]

    @pytest.mark.asyncio
    async def test_get_national_data_by_question(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        # question not found
        res = await client.get(
            app.url_path_for(
                "charts:get_national_charts_by_question",
                question=12345
            )
        )
        assert res.status_code == 404
        # not number, multiple, option question
        res = await client.get(
            app.url_path_for(
                "charts:get_national_charts_by_question",
                question=638730937
            )
        )
        assert res.status_code == 404
        # number question
        res = await client.get(
            app.url_path_for(
                "charts:get_national_charts_by_question",
                question=624670928
            )
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'name': 'No. of classrooms',
            'total': 13.0,
            'count': 1
        }
        # option question
        res = await client.get(
            app.url_path_for(
                "charts:get_national_charts_by_question",
                question=624670933
            )
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'name': 'Type of power supply',
            'option': [{
                'name': 'Mains Electricity',
                'order': 1,
                'color': None,
                'description': None,
                'count': 1
            }, {
                'name': 'Solar',
                'order': 2,
                'color': None,
                'description': None,
                'count': 1
            }, {
                'name': 'Generator',
                'order': 3,
                'color': None,
                'description': None,
                'count': 1
            }, {
                'name': 'No power supply',
                'order': 4,
                'color': None,
                'description': None,
                'count': 0
            }, {
                'name': "Don't know / can't say",
                'order': 5,
                'color': None,
                'description': None,
                'count': 0
            }]
        }
