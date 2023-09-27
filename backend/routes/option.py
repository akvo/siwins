import os
from typing import List
from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db.connection import get_session
from db.crud_option import get_option_year_conducted

from source.main import main_config

MONITORING_ROUND = main_config.MONITORING_ROUND


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
    if os.environ["TESTING"]:
        MONITORING_ROUND = 2023
    options = get_option_year_conducted(session=session)
    if not options:
        return []
    options = [int(o.name) for o in options]
    options = list(filter(
        lambda x: (x <= MONITORING_ROUND), options
    ))
    options.sort()
    return options
