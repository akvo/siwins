from fastapi import (
    Depends, Request, APIRouter
)
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db.connection import get_session
from db.crud_sync import get_last_sync

security = HTTPBearer()
sync_route = APIRouter()


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
