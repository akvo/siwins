import os
import sys
import json
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from seeder.form import form_seeder
from seeder.datapoint import datapoint_seeder
from seeder.data_sync import data_sync, deleted_data_sync
from db import crud_sync
from db import crud_form
from db import crud_data

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


forms = []
forms_config = "./source/forms.json"
with open(forms_config) as json_file:
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

        form_seeder(session=session, token=token, forms=forms)
        datapoint_seeder(session=session, token=token, forms=forms)
        for form in forms:
            fid = form.get("id")
            check_form = crud_form.get_form_by_id(session=session, id=fid)
            assert check_form.id == fid

    @pytest.mark.asyncio
    async def test_get_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # registration data
        data = crud_data.get_all_data(session=session, registration=True)
        data = [d.serialize for d in data]
        assert data == [
            {
                "id": 642650980,
                "datapoint_id": 716330915,
                "identifier": "dfmn-hw5g-11se",
                "name": "SMA N 1 Nusa Penida - High school",
                "form": 733030972,
                "registration": True,
                "geo": {"lat": -8.676368333333333, "long": 115.49182166666667},
                "created": "December 01, 2022",
                "updated": "December 01, 2022",
                "answer": [
                    {"question": 718001069, "value": "High school"},
                    {
                        "question": 721880978,
                        "value": "-8.676368333333333|115.49182166666667",
                    },
                    {"question": 738940972, "value": "SMA N 1 Nusa Penida"},
                ],
                "history": [],
            }
        ]
        # monitoring data
        temp_data = crud_data.get_all_data(session=session, registration=False)
        data = [d.serialize for d in temp_data]
        assert data == [
            {
                "id": 729930913,
                "datapoint_id": 716330915,
                "identifier": "dfmn-hw5g-11se",
                "name": "SMA N 1 Nusa Penida - High school",
                "form": 729240983,
                "registration": False,
                "geo": None,
                "created": "December 01, 2022",
                "updated": "December 01, 2022",
                "answer": [],
                "history": [
                    {"question": 725310914, "value": 200.0},
                    {"question": 735090984, "value": 10.0},
                    {"question": 738950915, "value": "Clean"},
                ],
            },
            {
                "id": 733410921,
                "datapoint_id": 716330915,
                "identifier": "dfmn-hw5g-11se",
                "name": "SMA N 1 Nusa Penida - High school",
                "form": 729240983,
                "registration": False,
                "geo": None,
                "created": "December 01, 2022",
                "updated": "December 01, 2022",
                "answer": [
                    {"question": 725310914, "value": 225.0},
                    {"question": 735090984, "value": 15.0},
                    {"question": 738950915, "value": "Clean"},
                ],
                "history": [],
            },
        ]
        # monitoring format
        data = [d.to_monitoring_data for d in temp_data]
        assert data[0]["id"] == 729930913
        assert data[0]["name"] == "SMA N 1 Nusa Penida - High school"
        assert len(data[0]["monitoring"]) == 3

    @pytest.mark.asyncio
    async def test_sync(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        token = {"token": None, "time": 0}
        sync_data_file = "./source/static/sync_data.json"
        sync_data = {}
        with open(sync_data_file) as json_file:
            sync_data = json.load(json_file)
        data_sync(token=token, session=session, sync_data=sync_data)
        # monitoring data
        temp_data = crud_data.get_all_data(session=session, registration=False)
        # monitoring format
        data = [d.to_monitoring_data for d in temp_data]
        assert data[0]["id"] == 729930913
        assert data[0]["name"] == "SMA N 1 Nusa Penida - High school"
        assert len(data[0]["monitoring"]) == 3

    @pytest.mark.asyncio
    async def test_sync_deleted_data_monitoring_history(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        changes = {"formInstanceDeleted": [754830913]}
        data = changes.get("formInstanceDeleted")
        deleted_data_sync(session=session, data=data)
        monitoring = crud_data.get_all_data(
            session=session, registration=False
        )
        rs = [m.serialize for m in monitoring]
        assert data[0] not in [r["id"] for r in rs]
