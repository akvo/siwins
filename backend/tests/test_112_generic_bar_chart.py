import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from models.question import QuestionAttributes

pytestmark = pytest.mark.asyncio
sys.path.append("..")


class TestGenericBarChartRoutes:
    @pytest.mark.asyncio
    async def test_get_generic_bar_chart_question(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # filter by question attribute
        res = await client.get(
            app.url_path_for("question:get_all_question"),
            params={"attribute": QuestionAttributes.generic_bar_chart.value}
        )
        assert res.status_code == 200
        res = res.json()
        name = 'In the previous two weeks, was drinking water from the main '
        name += 'source available at the school throughout each school day?'
        display_name = 'Water availability at primary source '
        display_name += 'in previous two weeks'
        assert res[0] == {
            'id': 624660930,
            'name': name,
            "display_name": display_name,
            "type": "option",
            'attributes': ['indicator', 'advance_filter', 'generic_bar_chart'],
            'option': [{
                "name": "Yes",
                "order": 1,
                "color": "#2EA745",
                "description": "Example of Yes info text"
            }, {
                "name": "No",
                "order": 2,
                "color": "#DC3545",
                "description": "Example No of info text"
            }, {
                "name": "Don't know/can't say",
                "order": 3,
                "color": "#666666",
                "description": "Example of Don't know/can't say info text"
            }],
            'number': []
        }

    @pytest.mark.asyncio
    async def test_get_generic_bar_chart_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        # no filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930)
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'type': 'BAR',
            'data': [{'name': 'no', 'value': 1}]
        }
        # with stack = question
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={"stack": 624660930}
        )
        assert res.status_code == 406
        # with stack != question
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={"stack": 624660927}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'type': 'BARSTACK',
            'data': [
                {
                    'group': 'no',
                    'child': [
                        {
                            'name': 'mostly (unavailable ≤ 30 days total)',
                            'value': 1
                        }
                    ]
                }
            ]
        }
        # with indicator
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={"indicator": 624660930}
        )
        assert res.status_code == 200
        # with indicator & indicator option filter
        # option indicator with number filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={"indicator": 624660930, "number": [10, 20]}
        )
        assert res.status_code == 400
        # option indicator with option filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={"indicator": 624660930, "q": "624660930|yes"}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {'type': 'BAR', 'data': []}
        # number indicator with number filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={"indicator": 630020919, "number": [11]}
        )
        assert res.status_code == 400
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={"indicator": 630020919, "number": [1, 20]}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'type': 'BAR',
            'data': [{'name': 'no', 'value': 1}]
        }
        # filter by school type and province
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={
                "prov": ["Guadalcanal"],
                "sctype": ["Community High School"]
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'type': 'BAR',
            'data': [{'name': 'no', 'value': 1}]
        }
        # with stack != question and filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=624660930),
            params={
                "stack": 624660927,
                "prov": ["Guadalcanal"],
                "sctype": ["Community High School"]
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'type': 'BARSTACK',
            'data': [
                {
                    'group': 'no',
                    'child': [
                        {
                            'name': 'mostly (unavailable ≤ 30 days total)',
                            'value': 1
                        }
                    ]
                }
            ]
        }
