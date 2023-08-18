import os
import json
import flow.auth as flow_auth
from fastapi import (
    Depends, Request, APIRouter,
    BackgroundTasks
)
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db.connection import get_session
from db.crud_sync import get_last_sync
from seeder.data_sync import data_sync
from utils.functions import refresh_materialized_data
from utils.helper import write_log

security = HTTPBearer()
sync_route = APIRouter()


def run_force_sync(session: Session, last_sync: dict):
    TESTING = os.environ.get("TESTING")
    sync_data = None
    next_sync_url = last_sync.get('url')
    token = flow_auth.get_token()
    sync_data = flow_auth.get_data(url=next_sync_url, token=token)
    if sync_data:
        errors = data_sync(
            token=token,
            session=session,
            sync_data=sync_data
        )
        log_content = json.dumps(errors, indent=2)
        write_log(
            log_filename="sync_force_url_errors",
            log_content=log_content
        )
        if not TESTING:
            refresh_materialized_data()


@sync_route.get(
    "/cursor",
    name="sync:get_cursor",
    summary="get sync cursor",
    tags=["Sync"]
)
def get_sync_cursor(
    req: Request,
    session: Session = Depends(get_session)
):
    res = get_last_sync(session=session)
    if not res:
        return None
    return res.get_cursor


@sync_route.get(
    "/sync/force",
    name="sync:force",
    summary="force sync from url",
    tags=["Sync"]
)
def sync_force(
    req: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    TESTING = os.environ.get("TESTING")
    last_sync = get_last_sync(session=session)
    if not last_sync:
        return None
    last_sync = last_sync.serialize
    if TESTING:
        run_force_sync(session=session, last_sync=last_sync)
        return last_sync
    background_tasks.add_task(run_force_sync, session, last_sync)
    return last_sync
