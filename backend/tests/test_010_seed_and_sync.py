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

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


forms = []
forms_config = "./source/forms.json"
with open(forms_config) as json_file:
    forms = json.load(json_file)


class TestSeedAndSync():
    @pytest.mark.asyncio
    async def test_seed_form_and_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        token = {'token': None, 'time': 0}
        # init sync
        url = 'test init add sync url'
        sync_res = crud_sync.add_sync(session=session, url=url)
        last_sync = crud_sync.get_last_sync(session=session)
        assert last_sync.url == sync_res.url

        form_seeder(session=session, token=token, forms=forms)
        datapoint_seeder(session=session, token=token, forms=forms)
        for form in forms:
            fid = form.get('id')
            check_form = crud_form.get_form_by_id(
                session=session, id=fid)
            assert check_form.id == fid

    @pytest.mark.asyncio
    async def test_get_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # registration data
        data = crud_data.get_all_data(session=session, registration=True)
        data = [d.serialize for d in data]
        assert data == [{
            "id": 1,
            "datapoint_id": 716330915,
            "identifier": "dfmn-hw5g-11se",
            "name": "SMA N 1 Nusa Penida - High school",
            "form": 733030972,
            "registration": True,
            "geo": {
                "lat": -8.676368333333333,
                "long": 115.49182166666667
            },
            "created": "December 01, 2022",
            "updated": "December 01, 2022",
            "answer": [{
                "question": 718001069,
                "value": "High school"
            }, {
                "question": 721880978,
                "value": "-8.676368333333333|115.49182166666667"
            }, {
                "question": 738940972,
                "value": "SMA N 1 Nusa Penida"
            }]
        }]
        # monitoring data
        temp_data = crud_data.get_all_data(session=session, registration=False)
        data = [d.serialize for d in temp_data]
        assert data == [{
            "id": 2,
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
            ]
        }]
        # monitoring format
        data = [d.to_monitoring_data for d in temp_data]
        assert data == [{
            "id": 2,
            "name": "SMA N 1 Nusa Penida - High school",
            "monitoring": [{
                "history": False,
                "question_id": 725310914,
                "question": "Number students",
                "date": "Dec 01, 2022 - 3:03:25 AM",
                "type": "number",
                "value": 225.0,
            }, {
                "history": False,
                "question_id": 735090984,
                "question": "Number toilets",
                "date": "Dec 01, 2022 - 3:03:25 AM",
                "type": "number",
                "value": 15.0,
            }, {
                "history": False,
                "question_id": 738950915,
                "question": "Status of toilet",
                "date": "Dec 01, 2022 - 3:03:25 AM",
                "type": "option",
                "value": "Clean",
            }, {
                "history": True,
                "question_id": 725310914,
                "question": "Number students",
                "date": "Dec 01, 2022 - 3:02:59 AM",
                "type": "number",
                "value": 200.0,
            }, {
                "history": True,
                "question_id": 735090984,
                "question": "Number toilets",
                "date": "Dec 01, 2022 - 3:02:59 AM",
                "type": "number",
                "value": 10.0,
            }, {
                "history": True,
                "question_id": 738950915,
                "question": "Status of toilet",
                "date": "Dec 01, 2022 - 3:02:59 AM",
                "type": "option",
                "value": "Clean",
            }]
        }]

    @pytest.mark.asyncio
    async def test_sync(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        token = {'token': None, 'time': 0}
        sync_data_file = "./source/static/sync_data.json"
        sync_data = {}
        with open(sync_data_file) as json_file:
            sync_data = json.load(json_file)
        data_sync(token=token, session=session, sync_data=sync_data)
        # monitoring data
        temp_data = crud_data.get_all_data(session=session, registration=False)
        # monitoring format
        data = [d.to_monitoring_data for d in temp_data]
        assert data == [{
            "id": 2,
            "name": "SMA N 1 Nusa Penida - High school",
            "monitoring": [{
                "history": False,
                "question_id": 725310914,
                "question": "Number students",
                "date": "Dec 02, 2022 - 3:03:25 AM",
                "type": "number",
                "value": 100.0,
            }, {
                "history": False,
                "question_id": 735090984,
                "question": "Number toilets",
                "date": "Dec 02, 2022 - 3:03:25 AM",
                "type": "number",
                "value": 10.0,
            }, {
                "history": False,
                "question_id": 738950915,
                "question": "Status of toilet",
                "date": "Dec 02, 2022 - 3:03:25 AM",
                "type": "option",
                "value": "Clean",
            }, {
                "history": True,
                "question_id": 738950915,
                "question": "Status of toilet",
                "date": "Dec 02, 2022 - 3:02:59 AM",
                "type": "option",
                "value": "Clean",
            }, {
                "history": True,
                "question_id": 725310914,
                "question": "Number students",
                "date": "Dec 02, 2022 - 3:02:59 AM",
                "type": "number",
                "value": 110.0,
            }, {
                "history": True,
                "question_id": 735090984,
                "question": "Number toilets",
                "date": "Dec 02, 2022 - 3:02:59 AM",
                "type": "number",
                "value": 11.0,
            }, {
                "history": True,
                "question_id": 735090984,
                "question": "Number toilets",
                "date": "Dec 01, 2022 - 3:03:25 AM",
                "type": "number",
                "value": 15.0,
            }, {
                "history": True,
                "question_id": 725310914,
                "question": "Number students",
                "date": "Dec 01, 2022 - 3:03:25 AM",
                "type": "number",
                "value": 225.0,
            }, {
                "history": True,
                "question_id": 738950915,
                "question": "Status of toilet",
                "date": "Dec 01, 2022 - 3:03:25 AM",
                "type": "option",
                "value": "Clean",
            }, {
                "history": True,
                "question_id": 725310914,
                "question": "Number students",
                "date": "Dec 01, 2022 - 3:02:59 AM",
                "type": "number",
                "value": 200.0,
            }, {
                "history": True,
                "question_id": 738950915,
                "question": "Status of toilet",
                "date": "Dec 01, 2022 - 3:02:59 AM",
                "type": "option",
                "value": "Clean",
            }, {
                "history": True,
                "question_id": 735090984,
                "question": "Number toilets",
                "date": "Dec 01, 2022 - 3:02:59 AM",
                "type": "number",
                "value": 10.0,
            }]
        }]
