import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from models.question import QuestionAttributes

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestQuestionRoutes:
    @pytest.mark.asyncio
    async def test_get_question(
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
            "display_name": "Year of survey",
            "type": "option",
            "option": [{
                'name': '2018',
                'order': 1,
                'color': None,
                'description': None,
            }, {
                'name': '2023',
                'order': 2,
                'color': None,
                'description': None,
            }],
            "attributes": [],
            "number": []
        }
        # filter by question attribute
        res = await client.get(
            app.url_path_for("question:get_all_question"),
            params={"attribute": QuestionAttributes.indicator.value}
        )
        assert res.status_code == 200
        res = res.json()
        # JMP category in indicator dropdown
        assert res[:3] == [{
            'id': 'jmp-water',
            'name': 'Water',
            'type': 'jmp',
            'display_name': 'Water',
            'attributes': ['indicator'],
            'option': [{
                'name': 'Safely Managed',
                'order': 1,
                'color': '#0080c6',
                'description': None
            }, {
                'name': 'Basic',
                'order': 2,
                'color': '#00b8ec',
                'description': None
            }, {
                'name': 'Limited',
                'order': 3,
                'color': '#fff176',
                'description': None
            }, {
                'name': 'No Service',
                'order': 4,
                'color': '#FEBC11',
                'description': None
            }],
            'number': []
        }, {
            'id': 'jmp-sanitation',
            'name': 'Sanitation',
            'type': 'jmp',
            'display_name': 'Sanitation',
            'attributes': ['indicator'],
            'option': [{
                'name': 'Basic',
                'order': 1,
                'color': '#ab47bc',
                'description': None
            }, {
                'name': 'Limited',
                'order': 2,
                'color': '#fff176',
                'description': None
            }, {
                'name': 'No Service',
                'order': 3,
                'color': '#FEBC11',
                'description': None
            }],
            'number': []
        }, {
            'id': 'jmp-hygiene',
            'name': 'Hygiene',
            'type': 'jmp',
            'display_name': 'Hygiene',
            'attributes': ['indicator'],
            'option': [{
                'name': 'Basic',
                'order': 1,
                'color': '#51B453',
                'description': None
            }, {
                'name': 'Limited',
                'order': 2,
                'color': '#fff176',
                'description': None
            }, {
                'name': 'No Service',
                'order': 3,
                'color': '#FEBC11',
                'description': None
            }],
            'number': []
        }]
        name = 'In the previous two weeks, was drinking water from the main '
        name += 'source available at the school throughout each school day?'
        display_name = 'Water availability at primary source '
        display_name += 'in previous two weeks'
        assert res[3] == {
            'id': 624660930,
            'name': name,
            "display_name": display_name,
            "type": "option",
            'attributes': [
                'indicator',
                'advance_filter',
                'generic_bar_chart',
                'school_detail_popup'
            ],
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
        name = 'Is drinking water from the main source '
        name += 'typically available throughout the school year?'
        display_name = 'Water availability at primary source '
        display_name += 'throughout school year'
        assert res[4] == {
            'id': 624660927,
            'name': name,
            "display_name": display_name,
            "type": "option",
            'attributes': [
                'indicator',
                'advance_filter',
                'generic_bar_chart',
                'school_detail_popup'
            ],
            'option': [{
                'name': 'Yes (always available)',
                'order': 1,
                'color': None,
                'description': None,
            }, {
                'name': 'Mostly (unavailable ≤ 30 days total)',
                'order': 2,
                'color': None,
                'description': None,
            }, {
                'name': 'No (unavailable > 30 days total)',
                'order': 3,
                'color': None,
                'description': None,
            }, {
                'name': "Don't know/can't say",
                'order': 4,
                'color': None,
                'description': None,
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
