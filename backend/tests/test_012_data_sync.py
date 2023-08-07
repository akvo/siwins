import os
import sys
import json
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from seeder.data_sync import data_sync
from db import crud_data
from source.main_config import DATAPOINT_PATH
from tests.conftest import test_refresh_materialized_data
# from tests.test_dummy import res_sync_data, res_answers # TODO:: Delete

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDataSync:
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
        test_refresh_materialized_data()
        # current data
        temp_data = crud_data.get_all_data(session=session, current=True)
        data = [d.serialize for d in temp_data]
        assert list(data[0]) == [
            'id',
            'datapoint_id',
            'identifier',
            'name',
            'form',
            'registration',
            'current',
            'geo',
            'year_conducted',
            'school_information',
            'created',
            'updated',
            'answer',
            'history'
        ]
        assert data[0]["id"] == 649130936
        for d in data:
            d["current"] is True
        assert list(data[0]["answer"][0]) == ['question', 'value']
        # assert data == res_sync_data  # TODO:: Delete
        # monitoring data
        temp_data = crud_data.get_all_data(session=session, current=False)
        data = [d.serialize for d in temp_data]
        assert list(data[0]) == [
            'id',
            'datapoint_id',
            'identifier',
            'name',
            'form',
            'registration',
            'current',
            'geo',
            'year_conducted',
            'school_information',
            'created',
            'updated',
            'answer',
            'history'
        ]
        assert data[0]["id"] == 632510922
        for d in data:
            d["current"] is False
        assert list(data[0]["answer"][0]) == ['question', 'value']
        # TODO:: Delete
        # assert data == [
        #     {
        #         "id": 632510922,
        #         "datapoint_id": 624690917,
        #         "identifier": "d5bi-mkoi-qrej",
        #         "name": "Untitled",
        #         "form": 647170919,
        #         "registration": True,
        #         "current": False,
        #         "geo": {
        #             "lat": -47.72084919070232,
        #             "long": 71.64445931032847
        #         },
        #         "year_conducted": 2018,
        #         "school_information": [
        #             "Guadalcanal",
        #             "Community High School",
        #             "AO CHS",
        #             "21710",
        #         ],
        #         "created": "April 07, 2023",
        #         "updated": "April 07, 2023",
        #         "answer": res_answers,
        #         "history": [],
        #     }
        # ]
