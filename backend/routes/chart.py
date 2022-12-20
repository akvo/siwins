# from fastapi import Depends
from fastapi import APIRouter
from fastapi.security import HTTPBearer

# from sqlalchemy.orm import Session
# from db.connection import get_session

security = HTTPBearer()
chart_route = APIRouter()


@chart_route.get(
    "/chart/",
    name="charts:get",
    summary="get chart list",
    tags=["Charts"],
)
def get_chart():
    data = []
    return data


@chart_route.get(
    "/chart/{datapoint_id}",
    name="chart:get_chart_by_datapoint",
    summary="get chart by datapoint id",
    tags=["Charts"],
)
def get_chart_by_datapoint():
    return []
