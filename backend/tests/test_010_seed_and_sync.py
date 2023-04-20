import os
import sys
import json
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from seeder.form import form_seeder
from seeder.datapoint import datapoint_seeder
from seeder.data_sync import data_sync
from db import crud_sync
from db import crud_form
from db import crud_data
from tests.conftest import test_refresh_materialized_data
from source.main_config import FORM_CONFIG_PATH, DATAPOINT_PATH

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

res_answers = [{
    "question": 649140920,
    "value": "No"
}, {
    "question": 592240932,
    "value": "Sea"
}, {
    "question": 634450928,
    "value": "No"
}, {
    "question": 634450929,
    "value": "No"
}, {
    "question": 638730944,
    "value": "Yes"
}, {
    "question": 638730951,
    "value": "Yes"
}, {
    "question": 634450922,
    "value": "No"
}, {
    "question": 634450930,
    "value": "No"
}, {
    "question": 638730950,
    "value": "No"
}, {
    "question": 638790937,
    "value": "Water only"
}, {
    "question": 638790936,
    "value": "No"
}, {
    "question": 638790933,
    "value": "Bathing areas( private and secure, door and lock and hangers)",
}, {
    "question": 638790932,
    "value": "Yes"
}, {
    "question": 638790938,
    "value": "Yes, for free"
}, {
    "question": 624680925,
    "value": "No"
}, {
    "question": 624680923,
    "value": "E-Coli"
}, {
    "question": 624680928,
    "value": "No"
}, {
    "question": 624680926,
    "value": "No"
}, {
    "question": 624670931,
    "value": "Main"
}, {
    "question": 638730935,
    "value": 12.0
}, {
    "question": 638730931,
    "value": "Day School"
}, {
    "question": 638730937,
    "value": "Galih Akvo"
}, {
    "question": 624670935,
    "value": 100.0
}, {
    "question": 624670934,
    "value": 12.0
}, {
    "question": 638730934,
    "value": "12"
}, {
    "question": 638730930,
    "value": 89.0
}, {
    "question": 624670930,
    "value": 111.0
}, {
    "question": 624670933,
    "value": "Mains Electricity"
}, {
    "question": 624670926,
    "value": 7.0
}, {
    "question": 638730933,
    "value": ["Guadalcanal", "Community High School", "AO CHS", "21710"],
}, {
    "question": 624670927,
    "value": "Provincial Secondary School"
}, {
    "question": 638730929,
    "value": "Non-Functioning"
}, {
    "question": 624670932,
    "value": ""
}, {
    "question": 624670928,
    "value": 12.0
}, {
    "question": 638730936,
    "value": "-47.72084919070232|71.64445931032847"
}, {
    "question": 624670929,
    "value": ""
}, {
    "question": 638730932,
    "value": 21.0
}, {
    "question": 640620926,
    "value": "Protected/covered well with pump"
}, {
    "question": 640620927,
    "value": "On the premises of the school"
}, {
    "question": 640620928,
    "value": "Between 500 and 1000 meters/1km"
}, {
    "question": 640620929,
    "value": "Yes"
}, {
    "question": 638770930,
    "value": "No"
}, {
    "question": 624660927,
    "value": "Yes (always available)"
}, {
    "question": 624660928,
    "value": "No"
}, {
    "question": 624660930,
    "value": "No"
}, {
    "question": 642230925,
    "value": "2-4 days/week"
}, {
    "question": 654960929,
    "value": "2018"
}, {
    "question": 654960925,
    "value": "Galih Akvo"
}, {
    "question": 654960928,
    "value": "Tester"
}, {
    "question": 654960930,
    "value": "Wayan Akvo"
}, {
    "question": 654960926,
    "value": "Tester"
}, {
    "question": 654960927,
    "value": 89.0
}, {
    "question": 630020922,
    "value": "No"
}, {
    "question": 630020920,
    "value": "No"
}, {
    "question": 630020919,
    "value": 12.0
}]
res_data = [{
    "id": 632510922,
    "datapoint_id": 624690917,
    "identifier": "d5bi-mkoi-qrej",
    "name": "Untitled",
    "form": 647170919,
    "registration": True,
    "current": True,
    "geo": {
        'lat': -47.72084919070232,
        'long': 71.64445931032847
    },
    "year_conducted": 2018,
    "school_information": [
        'Guadalcanal',
        'Community High School',
        'AO CHS',
        '21710'],
    "created": "April 07, 2023",
    "updated": "April 07, 2023",
    "answer": res_answers,
    "history": [],
}]

res_sync_answers = [{
    "question": 592240932,
    "value": "River"
}, {
    "question": 649140920,
    "value": "No"
}, {
    "question": 634450930,
    "value": "No"
}, {
    "question": 638730950,
    "value": "No"
}, {
    "question": 634450928,
    "value": "No"
}, {
    "question": 634450929,
    "value": "No"
}, {
    "question": 638730944,
    "value": "No"
}, {
    "question": 638730951,
    "value": "No"
}, {
    "question": 634450922,
    "value": "No"
}, {
    "question": 638790937,
    "value": "Water only"
}, {
    "question": 638790936,
    "value": "No"
}, {
    "question": 638790933,
    "value": "MHM materials (e.g. pads)"
}, {
    "question": 638790932,
    "value": "No"
}, {
    "question": 638790938,
    "value": "Yes, for purchase"
}, {
    "question": 624680924,
    "value": "No"
}, {
    "question": 624680925,
    "value": "No"
}, {
    "question": 624680923,
    "value": "Arsenic"
}, {
    "question": 624680928,
    "value": "No"
}, {
    "question": 624670931,
    "value": "Main"
}, {
    "question": 638730935,
    "value": 22.0
}, {
    "question": 638730931,
    "value": "Day School"
}, {
    "question": 638730937,
    "value": "Wayan"
}, {
    "question": 624670935,
    "value": 111.0
}, {
    "question": 624670934,
    "value": 21.0
}, {
    "question": 638730934,
    "value": "31"
}, {
    "question": 638730930,
    "value": 98.0
}, {
    "question": 624670930,
    "value": 123.0
}, {
    "question": 624670933,
    "value": "Mains Electricity"
}, {
    "question": 624670926,
    "value": 7.0
}, {
    "question": 638730933,
    "value": ["Guadalcanal", "Community High School", "AO CHS", "21710"],
}, {
    "question": 624670927,
    "value": "Community High School"
}, {
    "question": 638730929,
    "value": "Functioning"
}, {
    "question": 624670932,
    "value": ""
}, {
    "question": 624670928,
    "value": 13.0
}, {
    "question": 638730936,
    "value": "-51.14834033402119|41.7559732176761"
}, {
    "question": 624670929,
    "value": ""
}, {
    "question": 638730932,
    "value": 22.0
}, {
    "question": 640620926,
    "value": "Protected/covered well with pump"
}, {
    "question": 640620927,
    "value": "Between 500 and 1000 meters/1km of school premises",
}, {
    "question": 640620928,
    "value": "Between 500 and 1000 meters/1km"
}, {
    "question": 640620929,
    "value": "No"
}, {
    "question": 638770930,
    "value": "No"
}, {
    "question": 624660927,
    "value": "Mostly (unavailable ≤ 30 days total)"
}, {
    "question": 624660928,
    "value": "No"
}, {
    "question": 624660930,
    "value": "No"
}, {
    "question": 642230925,
    "value": "2-4 days/week"
}, {
    "question": 654960929,
    "value": "2023"
}, {
    "question": 654960925,
    "value": "Galih Akvo"
}, {
    "question": 654960928,
    "value": "Tester"
}, {
    "question": 654960930,
    "value": "Wayan Akvo"
}, {
    "question": 654960926,
    "value": "Tester"
}, {
    "question": 654960927,
    "value": 89.0
}, {
    "question": 630020922,
    "value": "No"
}, {
    "question": 630020920,
    "value": "No"
}, {
    "question": 630020919,
    "value": 12.0
}]

res_sync_data = [{
    "id": 649130936,
    "datapoint_id": 640630937,
    "identifier": "eptc-hraw-kkps",
    "name": "Untitled",
    "form": 647170919,
    "registration": True,
    "current": True,
    "geo": {"lat": -51.14834033402119, "long": 41.7559732176761},
    "year_conducted": 2023,
    "school_information": [
        "Guadalcanal",
        "Community High School",
        "AO CHS",
        "21710",
    ],
    "created": "April 07, 2023",
    "updated": None,
    "answer": res_sync_answers,
    "history": [],
}]


forms = []
with open(FORM_CONFIG_PATH) as json_file:
    forms = json.load(json_file)


class TestSeedAndSync:
    @pytest.mark.asyncio
    async def test_seed_form_and_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        token = {"token": None, "time": 0}
        # init sync
        url = "test init add sync url"
        sync_res = crud_sync.add_sync(session=session, url=url)
        last_sync = crud_sync.get_last_sync(session=session)
        assert last_sync.url == sync_res.url

        form_seeder(session=session, forms=forms)
        # enable datapoint seeder test
        datapoint_seeder(session=session, token=token, forms=forms)
        test_refresh_materialized_data()
        for form in forms:
            fid = form.get("id")
            check_form = crud_form.get_form_by_id(session=session, id=fid)
            assert check_form.id == fid

    @pytest.mark.asyncio
    async def test_get_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # current data
        data = crud_data.get_all_data(
            session=session, current=True)
        data = [d.serialize for d in data]
        assert data == res_data
        # monitoring data
        temp_data = crud_data.get_all_data(
            session=session, current=False)
        data = [d.serialize for d in temp_data]
        assert data == []

    @pytest.mark.asyncio
    async def test_sync(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        token = {"token": None, "time": 0}
        sync_data_file = f"{DATAPOINT_PATH}/sync_data.json"
        sync_data = {}
        with open(sync_data_file) as json_file:
            sync_data = json.load(json_file)
        data_sync(token=token, session=session, sync_data=sync_data)
        # current data
        temp_data = crud_data.get_all_data(
            session=session, current=True)
        data = [d.serialize for d in temp_data]
        assert data == res_sync_data
        # monitoring data
        temp_data = crud_data.get_all_data(
            session=session, current=False)
        data = [d.serialize for d in temp_data]
        assert data == [{
            "id": 632510922,
            "datapoint_id": 624690917,
            "identifier": "d5bi-mkoi-qrej",
            "name": "Untitled",
            "form": 647170919,
            "registration": True,
            "current": False,
            "geo": {
                'lat': -47.72084919070232,
                'long': 71.64445931032847
            },
            "year_conducted": 2018,
            "school_information": [
                'Guadalcanal',
                'Community High School',
                'AO CHS',
                '21710'],
            "created": "April 07, 2023",
            "updated": "April 07, 2023",
            "answer": res_answers,
            "history": [],
        }]
