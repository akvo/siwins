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
    async def test_sync(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        token = {'token': None, 'time': 0}
        sync_data_file = "./source/static/sync_data.json"
        sync_data = {}
        with open(sync_data_file) as json_file:
            sync_data = json.load(json_file)
        data_sync(token=token, session=session, sync_data=sync_data)
