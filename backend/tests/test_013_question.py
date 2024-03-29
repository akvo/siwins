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
        res = await client.get(app.url_path_for("question:get_all_question"))
        assert res.status_code == 200
        res = res.json()
        assert list(res[0]) == [
            "id",
            "group",
            "name",
            "type",
            "attributes",
            "option",
            "number",
        ]
        # TODO:: Delete
        # assert res[0] == {
        #     "id": 654960929,
        #     "group": "General Information",
        #     "name": "Year of survey",
        #     "type": "option",
        #     "option": [{
        #         'name': '2018',
        #         'order': 1,
        #         'color': None,
        #         'description': None,
        #     }, {
        #         'name': '2023',
        #         'order': 2,
        #         'color': None,
        #         'description': None,
        #     }],
        #     "attributes": [],
        #     "number": []
        # }
        # filter by question attribute
        res = await client.get(
            app.url_path_for("question:get_all_question"),
            params={"attribute": QuestionAttributes.indicator.value},
        )
        assert res.status_code == 200
        res = res.json()
        # JMP category in indicator dropdown
        assert res[:3] == [
            {
                "id": "jmp-water",
                "group": "JMP Indicator",
                "name": "Service level for Drinking Water",
                "type": "jmp",
                "attributes": ["indicator"],
                "option": [
                    {
                        "name": "Basic",
                        "order": 1,
                        "color": "#00b8ec",
                        "description": None,
                    },
                    {
                        "name": "Limited",
                        "order": 2,
                        "color": "#fff176",
                        "description": None,
                    },
                    {
                        "name": "No Service",
                        "order": 3,
                        "color": "#FEBC11",
                        "description": None,
                    },
                ],
                "number": [],
            },
            {
                "id": "jmp-sanitation",
                "group": "JMP Indicator",
                "name": "Service level for Sanitation",
                "type": "jmp",
                "attributes": ["indicator"],
                "option": [
                    {
                        "name": "Basic",
                        "order": 1,
                        "color": "#51B453",
                        "description": None,
                    },
                    {
                        "name": "Limited",
                        "order": 2,
                        "color": "#fff176",
                        "description": None,
                    },
                    {
                        "name": "No Service",
                        "order": 3,
                        "color": "#FEBC11",
                        "description": None,
                    },
                ],
                "number": [],
            },
            {
                "id": "jmp-hygiene",
                "group": "JMP Indicator",
                "name": "Service level for Hygiene",
                "type": "jmp",
                "attributes": ["indicator"],
                "option": [
                    {
                        "name": "Basic",
                        "order": 1,
                        "color": "#ab47bc",
                        "description": None,
                    },
                    {
                        "name": "Limited",
                        "order": 2,
                        "color": "#fff176",
                        "description": None,
                    },
                    {
                        "name": "No Service",
                        "order": 3,
                        "color": "#FEBC11",
                        "description": None,
                    },
                ],
                "number": [],
            },
        ]
        assert list(res[3]) == [
            "id",
            "group",
            "name",
            "type",
            "attributes",
            "option",
            "number",
        ]
        for r in res:
            if r["option"]:
                assert list(r["option"][0]) == [
                    "name",
                    "order",
                    "color",
                    "description",
                ]
            if r["type"] == "number":
                for x in r["number"]:
                    assert "value" in x
                    assert "count" in x
        # TODO:: Delete
        # name = 'In the previous two weeks, was drinking water from the main '
        # name += 'source available at the school throughout each school day?'
        # display_name = 'Water availability at primary source '
        # display_name += 'in previous two weeks'
        # assert res[3] == {
        #     'id': 624660930,
        #     'group': 'Water Availability',
        #     'name': display_name,
        #     "type": "option",
        #     'attributes': [
        #         'indicator',
        #         'advance_filter',
        #         'generic_bar_chart',
        #         'school_detail_popup'
        #     ],
        #     'option': [{
        #         "name": "Yes",
        #         "order": 1,
        #         "color": "#2EA745",
        #         "description": "Example of Yes info text"
        #     }, {
        #         "name": "No",
        #         "order": 2,
        #         "color": "#DC3545",
        #         "description": "Example No of info text"
        #     }, {
        #         "name": "Don't know/can't say",
        #         "order": 3,
        #         "color": "#666666",
        #         "description": "Example of Don't know/can't say info text"
        #     }],
        #     'number': []
        # }
        # # name = 'Is drinking water from the main source '
        # # name += 'typically available throughout the school year?'
        # display_name = 'Water availability at primary source '
        # display_name += 'throughout school year'
        # assert res[4] == {
        #     'id': 624660927,
        #     'group': 'Water Availability',
        #     'name': display_name,
        #     "type": "option",
        #     'attributes': [
        #         'indicator',
        #         'advance_filter',
        #         'generic_bar_chart',
        #         'school_detail_popup'
        #     ],
        #     'option': [{
        #         'name': 'Yes (always available)',
        #         'order': 1,
        #         'color': None,
        #         'description': None,
        #     }, {
        #         'name': 'Mostly (unavailable ≤ 30 days total)',
        #         'order': 2,
        #         'color': None,
        #         'description': None,
        #     }, {
        #         'name': 'No (unavailable > 30 days total)',
        #         'order': 3,
        #         'color': None,
        #         'description': None,
        #     }, {
        #         'name': "Don't know/can't say",
        #         'order': 4,
        #         'color': None,
        #         'description': None,
        #     }],
        #     'number': []
        # }
