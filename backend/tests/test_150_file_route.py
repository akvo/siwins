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
                'monitoring_round': None
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
                'monitoring_round': 2023
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
        res = res[0]
        status = JOB_STATUS_TEXT[JobStatus.done.value]
        assert res == {
            'id': 2,
            'status': status,
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
                'province': ['Guadalcanal'],
                'form_name': 'survey_questions',
                'school_type': None,
                'monitoring_round': 2023},
            'created': res.get('created'),
            'available': res.get('available')
        }

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
        res = await client.get(
            app.url_path_for(
                "excel-data:download",
                filename=filename
            )
        )
        assert res.status_code == 200
