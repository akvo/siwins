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
from db import crud_form
from db import crud_data
from tests.conftest import test_refresh_materialized_data

# from .test_dummy import res_data #TODO:: Delete

from source.main import main_config

FORM_CONFIG_PATH = main_config.FORM_CONFIG_PATH


sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


forms = []
with open(FORM_CONFIG_PATH) as json_file:
    forms = json.load(json_file)


class TestDataSeed:
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
        data = crud_data.get_all_data(session=session, current=True)
        data = [d.serialize for d in data]
        assert list(data[0]) == [
            "id",
            "datapoint_id",
            "identifier",
            "name",
            "form",
            "registration",
            "current",
            "geo",
            "year_conducted",
            "school_information",
            "created",
            "updated",
            "answer",
            "history",
        ]
        for d in data:
            d["current"] is True
        assert list(data[0]["answer"][0]) == ["question", "value"]
        # assert data == res_data #TODO:: Delete
        # monitoring data
        temp_data = crud_data.get_all_data(session=session, current=False)
        data = [d.serialize for d in temp_data]
        assert data == []
