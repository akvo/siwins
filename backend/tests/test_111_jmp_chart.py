import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session

pytestmark = pytest.mark.asyncio
sys.path.append("..")


res_jmp_no_fiter = {
    "question": "Sanitation",
    "data": [
        {
            "administration": "Malaita",
            "score": 0,
            "child": []},
        {
            "administration": "Rennell and Bellona",
            "score": 0,
            "child": []},
        {
            "administration": "Temotu",
            "score": 0,
            "child": []},
        {
            "administration": "Western",
            "score": 0,
            "child": []},
        {
            "administration": "Choiseul",
            "score": 0,
            "child": []},
        {
            "administration": "Guadalcanal",
            "score": 0,
            "child": [
                {
                    "option": "No Service",
                    "count": 1,
                    "percent": 100.0,
                    "color": None
                }
            ],
        },
        {
            "administration": "Honiara",
            "score": 0,
            "child": []},
        {
            "administration": "Isabel",
            "score": 0,
            "child": []},
        {
            "administration": "Makira and Ulawa",
            "score": 0,
            "child": []},
        {
            "administration": "Central",
            "score": 0,
            "child": []},
    ],
}

res_jmp_filtered = {
    "question": "Sanitation",
    "data": [
        {"administration": "Malaita", "score": 0, "child": []},
        {"administration": "Rennell and Bellona", "score": 0, "child": []},
        {"administration": "Temotu", "score": 0, "child": []},
        {"administration": "Western", "score": 0, "child": []},
        {"administration": "Choiseul", "score": 0, "child": []},
        {"administration": "Guadalcanal", "score": 0, "child": []},
        {"administration": "Honiara", "score": 0, "child": []},
        {"administration": "Isabel", "score": 0, "child": []},
        {"administration": "Makira and Ulawa", "score": 0, "child": []},
        {"administration": "Central", "score": 0, "child": []},
    ],
}


class TestJMPChartEndpoint:
    @pytest.mark.asyncio
    async def test_get_bar_charts_route(
        self, app: FastAPI, session: Session, client: AsyncClient
    ):
        # no filter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation")
        )
        assert res.status_code == 200
        res = res.json()
        assert res == res_jmp_no_fiter
        # with indicator
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": 624660930}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == res_jmp_no_fiter
        # with indicator & indicator option filter
        # option indicator with number filter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": 624660930, "number": [10, 20]}
        )
        assert res.status_code == 400
        # option indicator with option filter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": 624660930, "q": "624660930|no"}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == res_jmp_filtered
        # number indicator with number filter
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": 630020919, "number": [11]}
        )
        assert res.status_code == 400
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"indicator": 630020919, "number": [1, 20]}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == res_jmp_no_fiter
        # filter by province
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"prov": ["Central"]}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == res_jmp_filtered
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"prov": ["Guadalcanal"]}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == res_jmp_no_fiter
        # filter by school type
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"sctype": ["Primary School"]}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == res_jmp_filtered
        res = await client.get(
            app.url_path_for(
                "charts:get_aggregated_jmp_chart_data", type="Sanitation"),
            params={"sctype": ["Community High School"]}
        )
        assert res.status_code == 200
        res = res.json()
        assert res == res_jmp_no_fiter
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
        assert res == res_jmp_no_fiter
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
        assert res == res_jmp_filtered
