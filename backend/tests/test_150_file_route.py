import os
import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from models.jobs import JobStatus, JOB_STATUS_TEXT

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestFileRoutes:
    @pytest.mark.asyncio
    async def test_get_download_list_404(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("excel-data:download-list")
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_download_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # no filter
        res = await client.get(
            app.url_path_for("excel-data:generate")
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'id': 1,
            'status': 0,
            'payload': res.get('payload'),
            'info': {
                'tags': [],
                'options': None,
                'province': None,
                'form_name': 'survey_questions',
                'school_type': None,
                'monitoring_round': None,
                'data_ids': None
            },
            'created': res.get('created'),
            'available': None
        }
        # with filter
        res = await client.get(
            app.url_path_for("excel-data:generate"),
            params={
                "monitoring_round": 2023,
                "prov": ["Guadalcanal"]
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'id': 2,
            'status': 0,
            'payload': res.get('payload'),
            'info': {
                'tags': [{
                    'o': 2023,
                    'q': 'Monitoring round'
                }, {
                    'o': 'Guadalcanal',
                    'q': 'Province'
                }],
                'options': None,
                'province': ["Guadalcanal"],
                'form_name': 'survey_questions',
                'school_type': None,
                'monitoring_round': 2023,
                'data_ids': None
            },
            'created': res.get('created'),
            'available': None
        }
        # with data_ids only
        res = await client.get(
            app.url_path_for("excel-data:generate"),
            params={
                "data_ids": [649130936],
            }
        )
        assert res.status_code == 200
        res = res.json()
        assert res == {
            'id': 3,
            'status': 0,
            'payload': res.get('payload'),
            'info': {
                'tags': [],
                'options': None,
                'data_ids': ['649130936'],
                'province': None,
                'form_name': 'survey_questions',
                'school_type': None,
                'monitoring_round': None
            },
            'created': res.get('created'),
            'available': None
        }

    @pytest.mark.asyncio
    async def test_get_download_list(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(
            app.url_path_for("excel-data:download-list")
        )
        assert res.status_code == 200
        res = res.json()
        for r in res:
            assert "id" in r
            assert "status" in r
            assert "payload" in r
            assert "info" in r
            assert "tags" in r.get("info")
            assert "options" in r.get("info")
            assert "province" in r.get("info")
            assert "school_type" in r.get("info")
            assert "monitoring_round" in r.get("info")
            assert "created" in r
            assert "available" in r

    @pytest.mark.asyncio
    async def test_check_download_status(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # get file
        res = await client.get(
            app.url_path_for("excel-data:download-list")
        )
        assert res.status_code == 200
        res = res.json()
        res = res[0]
        # check status
        job_id = res.get("id")
        res = await client.get(
            app.url_path_for("excel-data:download-status"),
            params={"id": job_id}
        )
        assert res.status_code == 200
        r = res.json()
        assert "id" in r
        assert "status" in r
        assert "payload" in r
        assert "info" in r
        assert "tags" in r.get("info")
        assert "options" in r.get("info")
        assert "province" in r.get("info")
        assert "school_type" in r.get("info")
        assert "monitoring_round" in r.get("info")
        assert "created" in r
        assert "available" in r

    @pytest.mark.asyncio
    async def test_download_file(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        # get file
        res = await client.get(
            app.url_path_for("excel-data:download-list")
        )
        assert res.status_code == 200
        res = res.json()
        res = res[0]
        # download file
        filename = res.get('payload')
        status = res.get('status')
        if status == JOB_STATUS_TEXT.get(JobStatus.done.value):
            res = await client.get(
                app.url_path_for(
                    "excel-data:download",
                    filename=filename
                )
            )
            assert res.status_code == 200
