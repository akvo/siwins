from typing import List
from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db.connection import get_session
from db.crud_option import get_option_year_conducted


security = HTTPBearer()
option_route = APIRouter()


# Endpoint to fetch monitoring round
@option_route.get(
    "/option/monitoring_round",
    response_model=List[int],
    name="option:get_monitoring_round",
    summary="get monitoring round (year) values",
    tags=["Option"]
)
def get_option_monitoring_round(
    req: Request,
    session: Session = Depends(get_session)
):
    options = get_option_year_conducted(session=session)
    if not options:
        return []
    options = [int(o.name) for o in options]
    options.sort()
    return options