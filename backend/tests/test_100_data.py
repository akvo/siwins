import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from db import crud_data

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestDataRoutes:
    @pytest.mark.asyncio
    async def test_get_paginated_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # no filter
        res = await client.get(app.url_path_for("data:get_all"))
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == [
            'id', 'name', 'geo',
            'year_conducted', 'school_information'
        ]
        # filter with monitoring round
        res = await client.get(
            app.url_path_for("data:get_all"),
            params={"monitoring_round": 2010}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert res["data"] == []
        # filter with monitoring round
        # TODO: Delete
        # res_guadalcanal_chs_2018 = {
        #     'current': 1,
        #     'data': [{
        #         'id': 632510922,
        #         'name': 'Untitled',
        #         'geo': {
        #             'long': 71.64445931032847,
        #             'lat': -47.72084919070232
        #         },
        #         'year_conducted': 2018,
        #         'school_information': {
        #             'province': 'Guadalcanal',
        #             'school_type': 'Community High School',
        #             'school_name': 'AO CHS',
        #             'school_code': '21710'
        #         }
        #     }],
        #     'total': 1,
        #     'total_page': 1
        # }
        res = await client.get(
            app.url_path_for("data:get_all"),
            params={"monitoring_round": 2018}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == [
            'id', 'name', 'geo',
            'year_conducted', 'school_information'
        ]
        for d in res["data"]:
            assert d["year_conducted"] == 2018
        # assert res == res_guadalcanal_chs_2018 # TODO: Delete
        # filter with monitoring round, province, school_type
        res = await client.get(
            app.url_path_for("data:get_all"),
            params={
                "monitoring_round": 2018,
                "prov": "Central",
                "sctype": "Community High School"
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert res["data"] == []
        # filter with monitoring round, province, school_type
        res = await client.get(
            app.url_path_for("data:get_all"),
            params={
                "monitoring_round": 2018,
                "prov": "Guadalcanal",
                "sctype": "Community High School"
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == [
            'id', 'name', 'geo',
            'year_conducted', 'school_information'
        ]
        for d in res["data"]:
            assert d["year_conducted"] == 2018
        # filter with monitoring round, province, school_type
        res = await client.get(
            app.url_path_for("data:get_all"),
            params={
                "monitoring_round": 2018,
                "prov": "Guadalcanal",
                "sctype": "Primary School",
                "q": "624660930|no"
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert res["data"] == []

    @pytest.mark.asyncio
    async def test_get_answers_of_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("answer:get_data_answers", data_id=1234)
        )
        assert res.status_code == 404
        res = await client.get(
            app.url_path_for("answer:get_data_answers", data_id=649130936)
        )
        assert res.status_code == 200
        res = res.json()
        for r in res:
            assert "group" in r
            assert "child" in r
            for c in r.get("child"):
                assert "question_id" in c
                assert "question_name" in c
                assert "type" in c
                assert "value" in c

    @pytest.mark.asyncio
    async def test_get_init_maps_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("data:init_maps_data"),
            params={"page_only": True}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        # load all data
        res = await client.get(app.url_path_for("data:init_maps_data"))
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == [
            'id', 'school_information', 'year_conducted', 'geo'
        ]

    @pytest.mark.asyncio
    async def test_get_maps_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # without indicator
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"page_only": True}
        )
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        res = await client.get(app.url_path_for("data:get_maps_data"))
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO:: Delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'geo': [-51.14834033402119, 41.7559732176761],
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'answer': {}
        # }
        # with indicator
        indicator_id = 624660930
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id})
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO:: delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'geo': [-51.14834033402119, 41.7559732176761],
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'answer': {
        #         'question': 624660930,
        #         'value': 'No'
        #     }
        # }
        # with indicator & indicator option filter
        # option indicator with number filter
        indicator_id = 624660930
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id, "number": [10, 20]})
        assert res.status_code == 400
        # option indicator with option filter
        indicator_id = 624660930
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id, "q": f"{indicator_id}|no"})
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO:: Delete
        # assert res["data"] == [{
        #     'id': 649130936,
        #     'geo': [-51.14834033402119, 41.7559732176761],
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'answer': {
        #         'question': 624660930,
        #         'value': 'No'
        #     }
        # }]
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 624660930, "q": "624660930|yes"})
        assert res.status_code == 200
        res = res.json()
        assert res["data"] == []
        # number indicator with number filter
        indicator_id = 630020919
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id})
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO: Delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'geo': [-51.14834033402119, 41.7559732176761],
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'answer': {
        #         'question': 630020919,
        #         'value': 12
        #     }
        # }
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id, "number": [11]})
        assert res.status_code == 400
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id, "number": [1, 10]})
        assert res.status_code == 200
        res = res.json()
        assert res["data"] == []
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id, "number": [1, 20]})
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO: Delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'geo': [-51.14834033402119, 41.7559732176761],
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'answer': {
        #         'question': 630020919,
        #         'value': 12
        #     }
        # }
        # filter by province
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 630020919, "prov": ["Central"]})
        assert res.status_code == 200
        res = res.json()
        assert res["data"] == []
        # filter by province
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": 630020919, "prov": ["Guadalcanal"]})
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO:: delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'geo': [-51.14834033402119, 41.7559732176761],
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'answer': {
        #         'question': 630020919,
        #         'value': 12
        #     }
        # }
        # filter by school type
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={
                "indicator": 630020919,
                "sctype": ["Primary School"]
            })
        assert res.status_code == 200
        res = res.json()
        assert res["data"] == []
        # filter by school type
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={
                "indicator": 630020919,
                "sctype": ["Community High School"]
            })
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO:: delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'geo': [-51.14834033402119, 41.7559732176761],
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'answer': {
        #         'question': 630020919,
        #         'value': 12
        #     }
        # }
        # filter by school type and province
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={
                "indicator": 630020919,
                "prov": ["Central"],
                "sctype": ["Community High School"]
            })
        assert res.status_code == 200
        res = res.json()
        assert res["data"] == []
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={
                "indicator": 630020919,
                "prov": ["Guadalcanal"],
                "sctype": ["Community High School"]
            })
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO:: delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'geo': [-51.14834033402119, 41.7559732176761],
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'answer': {
        #         'question': 630020919,
        #         'value': 12
        #     }
        # }
        # JMP indicator
        indicator_id = "jmp-water"
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id})
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO: Delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'geo': [
        #         -51.14834033402119,
        #         41.7559732176761
        #     ],
        #     'answer': {
        #         'question': 'jmp-water_649130936',
        #         'value': 'Limited'
        #     }
        # }
        # JMP indicator filter by JMP level
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id, "q": "jmp-water|basic"})
        assert res.status_code == 200
        res = res.json()
        assert res["data"] == []
        res = await client.get(
            app.url_path_for("data:get_maps_data"),
            params={"indicator": indicator_id, "q": "jmp-water|limited"})
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'current', 'data', 'total', 'total_page'
        ]
        assert list(res["data"][0]) == ['id', 'answer']
        # TODO: Delete
        # assert res["data"][0] == {
        #     'id': 649130936,
        #     'school_information': {
        #         'province': 'Guadalcanal',
        #         'school_type': 'Community High School',
        #         'school_name': 'AO CHS',
        #         'school_code': '21710'
        #     },
        #     'year_conducted': 2023,
        #     'geo': [
        #         -51.14834033402119,
        #         41.7559732176761
        #     ],
        #     'answer': {
        #         'question': 'jmp-water_649130936',
        #         'value': 'Limited'
        #     }
        # }

    @pytest.mark.asyncio
    async def test_get_chart_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # get chart data without query params
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980)
        )
        assert res.status_code == 404
        # get chart data with history param True
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"history": True},
        )
        assert res.status_code == 404
        # get chart data with question_ids param
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"question_ids": [735090984]},
        )
        assert res.status_code == 404
        # get chart data with question_ids and history param
        res = await client.get(
            app.url_path_for("data:get_chart_data", data_id=642650980),
            params={"question_ids": [735090984], "history": True},
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_get_last_history_empty(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        fd = crud_data.get_last_history(
            session=session, datapoint_id=642770963, id=754830913
        )
        assert fd == []
