from http import HTTPStatus
from fastapi import Depends, Request
from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db.connection import get_session
from db.crud_data import (get_data_by_id)


security = HTTPBearer()
answer_route = APIRouter()


# TODO: Create new endpoint to fetch answer history
# ADD cascades level to config.js
@answer_route.get(
    "/answer/history/{data_id:path}",
    # response_model=List[CascadeNameAndLevel],
    name="answer:get_history",
    summary="get answet history by question & datapoint",
    tags=["Answer"]
)
def get_answer_history(
    req: Request,
    data_id: int,
    question_id: int,
    session: Session = Depends(get_session)
):
    data = get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    current_school = data.school_information
    current_year = data.year_conducted
    # get history datapoint by
    # current school and !current year / current = False

    return []
