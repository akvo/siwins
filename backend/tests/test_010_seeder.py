import os
import sys
import json
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from seeder.form import form_seeder
from seeder.datapoint import datapoint_seeder
from db import crud_sync

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


forms = []
forms_config = "./source/forms.json"
with open(forms_config) as json_file:
    forms = json.load(json_file)


class TestSeeder():
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
