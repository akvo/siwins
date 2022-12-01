# from http import HTTPStatus
# from datetime import datetime
from fastapi import Depends, Request, APIRouter
from fastapi.security import HTTPBearer
# from fastapi.security import HTTPBasicCredentials as credentials
from typing import List
from sqlalchemy.orm import Session
from db import crud_data
from db.connection import get_session
from models.data import MapsData

security = HTTPBearer()
data_route = APIRouter()


@data_route.get(
    "/maps/",
    response_model=List[MapsData],
    name="data:get_maps_data",
    summary="get maps data",
    tags=["Data"])
def get(
    req: Request,
    session: Session = Depends(get_session),
    # credentials: credentials = Depends(security)
):
    data = crud_data.get_all_data(session=session, registration=True)
    data = [d.to_maps for d in data]
    return data
