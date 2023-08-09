import os
import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from db.crud_sync import add_sync

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# static sync URL for test
cursor = "2635395"
url = "https://api-auth0.akvo.org/flow/orgs/sig/sync"
url += f"?next=true&cursor={cursor}"


class TestSyncRoutes:
    @pytest.mark.asyncio
    async def test_get_sync_cursor(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("sync:get_cursor"))
        assert res.status_code == 200
        res = res.json()
        assert res is None

        # add data to sync table
        save_sync = add_sync(session=session, url=url)
        assert save_sync.url == url

        res = await client.get(app.url_path_for("sync:get_cursor"))
        assert res.status_code == 200
        res = res.json()
        assert res == cursor

    @pytest.mark.asyncio
    async def test_force_sync_url(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("sync:force"))
        assert res.status_code == 200
        res = res.json()
        assert res == {"id": 2, "url": url}
