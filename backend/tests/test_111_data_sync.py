import os
import sys
import json
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from seeder.data_sync import data_sync, deleted_data_sync
from db import crud_data
from source.main_config import DATAPOINT_PATH
from .test_dummy import res_sync_data, res_answers

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
        # current data
        temp_data = crud_data.get_all_data(session=session, current=True)
        data = [d.serialize for d in temp_data]
        assert data == res_sync_data
        # monitoring data
        temp_data = crud_data.get_all_data(session=session, current=False)
        data = [d.serialize for d in temp_data]
        assert data == [
            {
                "id": 632510922,
                "datapoint_id": 624690917,
                "identifier": "d5bi-mkoi-qrej",
                "name": "Untitled",
                "form": 647170919,
                "registration": True,
                "current": False,
                "geo": {"lat": -47.72084919070232, "long": 71.64445931032847},
                "year_conducted": 2018,
                "school_information": [
                    "Guadalcanal",
                    "Community High School",
                    "AO CHS",
                    "21710",
                ],
                "created": "April 07, 2023",
                "updated": "April 07, 2023",
                "answer": res_answers,
                "history": [],
            }
        ]

    # @pytest.mark.asyncio
    async def test_sync_deleted_data_monitoring_history(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        changes = {"formInstanceDeleted": [649130936]}
        data = changes.get("formInstanceDeleted")
        deleted_data_sync(session=session, data=data)
        data = crud_data.get_all_data(session=session)
        rd = [m.serialize for m in data]
        assert data[0] not in [r["id"] for r in rd]
