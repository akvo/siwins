import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from tests.test_jmp_dummy import res_jmp_no_fiter, res_jmp_filtered

pytestmark = pytest.mark.asyncio
sys.path.append("..")


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
