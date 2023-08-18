import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from models.question import Question, QuestionType, QuestionAttributes
# from tests.test_jmp_dummy import (
#     res_jmp_no_fiter,
#     res_jmp_filtered,
#     res_jmp_filter_by_prov_sc_type,
#     res_jmp_history_no_filter
# ) # TODO:: Delete

pytestmark = pytest.mark.asyncio
sys.path.append("..")


class TestJMPChartRoutes:
    @pytest.mark.asyncio
    async def test_get_jmp_charts_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        # no filter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation")
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == ['question', 'data']
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_no_fiter
        # show history
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"
            ),
            params={"history": True}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_history_no_filter
        # with indicator
        indicator_question = session.query(Question).filter(
            Question.attributes.contains([QuestionAttributes.indicator.value])
        )
        indicator_option = indicator_question.filter(
            Question.type == QuestionType.option
        ).first()
        indicator_number = indicator_question.filter(
            Question.type == QuestionType.number
        ).first()

        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": indicator_option.id}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_no_fiter
        # with indicator & indicator option filter
        # option indicator with number filter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": indicator_option.id, "number": [10, 20]}
        )
        assert res.status_code == 400
        # option indicator with option filter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={
                "indicator": indicator_option.id,
                "q": f"{indicator_option.id}|no"
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_filtered
        # number indicator with number filter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": indicator_number.id, "number": [11]}
        )
        assert res.status_code == 400
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": indicator_number.id, "number": [1, 20]}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_no_fiter
        # filter by province
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"prov": ["Central"]}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        for d in res["data"]:
            if d["administration"] == "Central":
                continue
            for c in d["child"]:
                assert c["count"] == 0
        # TODO:: Delete
        # assert res == res_jmp_filter_by_prov_sc_type
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"prov": ["Guadalcanal"]}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        for d in res["data"]:
            if d["administration"] == "Guadalcanal":
                continue
            for c in d["child"]:
                assert c["count"] == 0
        # TODO:: Delete
        # assert res == res_jmp_no_fiter
        # filter by school type
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"sctype": ["Primary School"]}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_filter_by_prov_sc_type
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"sctype": ["Community High School"]}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_no_fiter
        # filter by school type and province
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={
                "prov": ["Guadalcanal"],
                "sctype": ["Community High School"]
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_no_fiter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={
                "prov": ["Central"],
                "sctype": ["Community High School"]
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res["data"][0]) == [
            'year', 'history', 'administration',
            'score', 'child'
        ]
        assert list(res["data"][0]["child"][0]) == [
            'option', 'count', 'percent', 'color', 'order'
        ]
        # TODO:: Delete
        # assert res == res_jmp_filter_by_prov_sc_type
