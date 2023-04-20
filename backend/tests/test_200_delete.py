import os
import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from seeder.data_sync import deleted_data_sync
from db import crud_data

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDelete:
    # @pytest.mark.asyncio
    async def test_sync_deleted_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        changes = {"formInstanceDeleted": [649130936]}
        data = changes.get("formInstanceDeleted")
        deleted_data_sync(session=session, data=data)
        data = crud_data.get_all_data(session=session)
        rd = [m.serialize for m in data]
        assert data[0] not in [r["id"] for r in rd]
