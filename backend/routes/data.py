from http import HTTPStatus
# from datetime import datetime
from fastapi import Depends, Request
from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
# from fastapi.security import HTTPBasicCredentials as credentials
from typing import List
from sqlalchemy.orm import Session
from db import crud_data
from db.connection import get_session
from models.data import MapsData, MonitoringData

security = HTTPBearer()
data_route = APIRouter()


@data_route.get(
    "/data/maps/",
    response_model=List[MapsData],
    name="data:get_maps_data",
    summary="get maps data",
    tags=["Data"])
def get_maps(
    req: Request,
    session: Session = Depends(get_session),
    # credentials: credentials = Depends(security)
):
    data = crud_data.get_all_data(session=session, registration=True)
    data = [d.to_maps for d in data]
    return data


@data_route.get(
    "/data/chart/{data_id}",
    response_model=MonitoringData,
    name="data:get_data_detail",
    summary="get data registration and monitoring detail",
    tags=["Data"])
def get_data_detail(
    req: Request,
    data_id: int,
    session: Session = Depends(get_session)
):
    # get registration data
    data = crud_data.get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Data not found")
    # get monitoring data for that datapoint
    monitoring_data = crud_data.get_monitoring_data(
        session=session, identifier=data.identifier)
    monitoring = []
    monitoring_data = [m.to_monitoring_data for m in monitoring_data]
    for md in monitoring_data:
        for m in md.get('monitoring'):
            monitoring.append(m)
    return {
        "id": data.id,
        "name": data.name,
        "monitoring": monitoring
    }
