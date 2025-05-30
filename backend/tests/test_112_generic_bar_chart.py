import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from models.question import Question, QuestionType, QuestionAttributes

pytestmark = pytest.mark.asyncio
sys.path.append("..")


res_bar = {
    "type": "BAR",
    "data": [
        {"year": 2023, "history": False, "name": "yes", "value": 0},
        {"year": 2023, "history": False, "name": "no", "value": 1},
        {
            "year": 2023,
            "history": False,
            "name": "don't know/can't say",
            "value": 0,
        },
    ],
}


res_bar_history = {
    "type": "BAR",
    "data": [
        {"year": 2018, "history": True, "name": "yes", "value": 0},
        {"year": 2018, "history": True, "name": "no", "value": 1},
        {
            "year": 2018,
            "history": True,
            "name": "don't know/can't say",
            "value": 0,
        },
    ],
}


res_bar_filtered = {
    "type": "BAR",
    "data": [
        {"year": 2023, "history": False, "name": "yes", "value": 0},
        {"year": 2023, "history": False, "name": "no", "value": 0},
        {
            "year": 2023,
            "history": False,
            "name": "don't know/can't say",
            "value": 0,
        },
    ],
}


res_bar_stack = {
    "type": "BARSTACK",
    "data": [
        {
            "year": 2023,
            "history": False,
            "group": "yes",
            "child": [
                {"name": "yes (always available)", "value": 0},
                {"name": "mostly (unavailable ≤ 30 days total)", "value": 0},
                {"name": "no (unavailable > 30 days total)", "value": 0},
                {"name": "don't know/can't say", "value": 0},
            ],
        },
        {
            "year": 2023,
            "history": False,
            "group": "no",
            "child": [
                {"name": "yes (always available)", "value": 0},
                {"name": "mostly (unavailable ≤ 30 days total)", "value": 1},
                {"name": "no (unavailable > 30 days total)", "value": 0},
                {"name": "don't know/can't say", "value": 0},
            ],
        },
        {
            "year": 2023,
            "history": False,
            "group": "don't know/can't say",
            "child": [
                {"name": "yes (always available)", "value": 0},
                {"name": "mostly (unavailable ≤ 30 days total)", "value": 0},
                {"name": "no (unavailable > 30 days total)", "value": 0},
                {"name": "don't know/can't say", "value": 0},
            ],
        },
    ],
}


res_bar_stack_history = {
    "type": "BARSTACK",
    "data": [
        {
            "year": 2018,
            "history": True,
            "group": "yes",
            "child": [
                {"name": "yes (always available)", "value": 0},
                {"name": "mostly (unavailable ≤ 30 days total)", "value": 0},
                {"name": "no (unavailable > 30 days total)", "value": 0},
                {"name": "don't know/can't say", "value": 0},
            ],
        },
        {
            "year": 2018,
            "history": True,
            "group": "no",
            "child": [
                {"name": "yes (always available)", "value": 1},
                {"name": "mostly (unavailable ≤ 30 days total)", "value": 0},
                {"name": "no (unavailable > 30 days total)", "value": 0},
                {"name": "don't know/can't say", "value": 0},
            ],
        },
        {
            "year": 2018,
            "history": True,
            "group": "don't know/can't say",
            "child": [
                {"name": "yes (always available)", "value": 0},
                {"name": "mostly (unavailable ≤ 30 days total)", "value": 0},
                {"name": "no (unavailable > 30 days total)", "value": 0},
                {"name": "don't know/can't say", "value": 0},
            ],
        },
    ],
}


class TestGenericBarChartRoutes:
    @pytest.mark.asyncio
    async def test_get_generic_bar_chart_question(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # filter by question attribute
        attribute = QuestionAttributes.generic_bar_chart.value
        res = await client.get(
            app.url_path_for("question:get_all_question"),
            params={"attribute": attribute},
        )
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
        assert attribute in res[0]["attributes"]
        assert list(res[0]["option"][0]) == [
            "name",
            "order",
            "color",
            "description",
        ]
        # TODO:: Delete
        # name = 'In the previous two weeks, was drinking water from the main '
        # name += 'source available at the school throughout each school day?'
        # display_name = 'Water availability at primary source '
        # display_name += 'in previous two weeks'
        # assert res[0] == {
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

    @pytest.mark.asyncio
    async def test_get_generic_bar_chart_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        indicator_question = session.query(Question).filter(
            Question.attributes.contains([QuestionAttributes.indicator.value])
        )
        indicator_option = indicator_question.filter(
            Question.type == QuestionType.option
        ).first()
        second_indicator = (
            indicator_question.filter(Question.type == QuestionType.option)
            .filter(Question.id != indicator_option.id)
            .first()
        )
        indicator_number = indicator_question.filter(
            Question.type == QuestionType.number
        ).first()
        # no filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            )
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ["type", "data"]
        assert res["type"] == "BAR"
        assert list(res["data"][0]) == ["year", "history", "name", "value"]
        for d in res["data"]:
            assert d["history"] is False
        # TODO:: Delete
        # assert res == res_bar
        # history data
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={"history": True},
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ["type", "data"]
        assert res["type"] == "BAR"
        # assert list(res["data"][0]) == ["year", "history", "name", "value"]
        # for d in res["data"]:
        #     assert d["history"] is True
        # TODO:: Delete
        # assert res == res_bar_history
        # with stack = question
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={"stack": indicator_option.id},
        )
        assert res.status_code == 406
        # with stack != question
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={"stack": second_indicator.id},
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ["type", "data"]
        assert res["type"] == "BARSTACK"
        assert list(res["data"][0]) == ["year", "history", "group", "child"]
        assert list(res["data"][0]["child"][0]) == ["name", "value"]
        for d in res["data"]:
            assert d["history"] is False
        # TODO:: Delete
        # assert res == res_bar_stack
        # show history with stack
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={"stack": second_indicator.id, "history": True},
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ["type", "data"]
        assert res["type"] == "BARSTACK"
        # assert list(res["data"][0]) == ["year", "history", "group", "child"]
        # assert list(res["data"][0]["child"][0]) == ["name", "value"]
        # for d in res["data"]:
        #     assert d["history"] is True
        # TODO:: Delete
        # assert res == res_bar_stack_history
        # with indicator
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={"indicator": indicator_option.id},
        )
        assert res.status_code == 200
        # with indicator & indicator option filter
        # option indicator with number filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={"indicator": indicator_option.id, "number": [10, 20]},
        )
        assert res.status_code == 400
        # option indicator with option filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={
                "indicator": indicator_option.id,
                "q": f"{indicator_option.id}|yes",
            },
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ["type", "data"]
        assert res["type"] == "BAR"
        assert list(res["data"][0]) == ["year", "history", "name", "value"]
        # TODO:: Delete
        # assert res == res_bar_filtered
        # number indicator with number filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={"indicator": indicator_number.id, "number": [11]},
        )
        assert res.status_code == 400
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={"indicator": indicator_number.id, "number": [1, 20]},
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ["type", "data"]
        assert res["type"] == "BAR"
        assert list(res["data"][0]) == ["year", "history", "name", "value"]
        # TODO:: Delete
        # assert res == res_bar
        # filter by school type and province
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={
                "prov": ["Guadalcanal"],
                "sctype": ["Community High School"],
            },
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ["type", "data"]
        assert res["type"] == "BAR"
        assert list(res["data"][0]) == ["year", "history", "name", "value"]
        # TODO:: Delete
        # assert res == res_bar
        # with stack != question and filter
        res = await client.get(
            app.url_path_for(
                "charts:get_generic_chart_data", question=indicator_option.id
            ),
            params={
                "stack": second_indicator.id,
                "prov": ["Guadalcanal"],
                "sctype": ["Community High School"],
            },
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ["type", "data"]
        assert res["type"] == "BARSTACK"
        assert list(res["data"][0]) == ["year", "history", "group", "child"]
        assert list(res["data"][0]["child"][0]) == ["name", "value"]
        # TODO:: Delete
        # assert res == res_bar_stack
