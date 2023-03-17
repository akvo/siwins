from http import HTTPStatus
from fastapi import Depends, Request
from fastapi import APIRouter, HTTPException, Query
from fastapi.security import HTTPBearer

# from fastapi.security import HTTPBasicCredentials as credentials
from typing import List, Optional
from sqlalchemy.orm import Session
from db import crud_data, crud_answer
from db.connection import get_session
from models.data import MapsData, MonitoringData
from models.data import DataDetail
from models.answer import Answer
from models.history import History

security = HTTPBearer()
data_route = APIRouter()


@data_route.get(
    "/data/maps",
    response_model=List[MapsData],
    name="data:get_maps_data",
    summary="get maps data",
    tags=["Data"],
)
def get_maps(
    req: Request,
    session: Session = Depends(get_session),
    indicator: int = Query(None)
    # credentials: credentials = Depends(security)
):
    data = crud_data.get_all_data(session=session, registration=True)
    data = [d.to_maps for d in data]
    # TODO:: how about the history ?
    for d in data:
        d["answer"] = [{
            "question": 1,
            "value": 50
        }]
    return data


@data_route.get(
    "/data/chart/{data_id}",
    response_model=MonitoringData,
    name="data:get_chart_data",
    summary="get monitoring data for chart",
    tags=["Data"],
)
def get_data_detail(
    req: Request,
    data_id: int,
    question_ids: Optional[List[int]] = Query(default=None),
    history: Optional[bool] = Query(default=False),
    session: Session = Depends(get_session),
):
    # get registration data
    data = crud_data.get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    # get monitoring data for that datapoint
    monitoring_data = crud_data.get_monitoring_data(
        session=session, identifier=data.identifier
    )
    monitoring_data_ids = [md.id for md in monitoring_data]
    # get answers
    answers = session.query(Answer).filter(
        Answer.data.in_(monitoring_data_ids)
    )
    if question_ids:
        answers = answers.filter(Answer.question.in_(question_ids))
    answers = answers.all()
    answers = [a.to_monitoring for a in answers]
    # get histories
    histories = None
    if history:
        histories = session.query(History).filter(
            History.data.in_(monitoring_data_ids)
        )
    if history and question_ids:
        histories = histories.filter(History.question.in_(question_ids))
    if history:
        histories = histories.all()
        histories = [h.to_monitoring for h in histories]
    # merge monitoring data
    monitoring = answers
    if histories:
        monitoring = answers + histories
    return {
        "id": data.id,
        "name": data.name,
        "monitoring": monitoring,
    }


@data_route.get(
    "/data/{datapoint_id}",
    response_model=DataDetail,
    name="data:get_data_detail",
    summary="get data detail by data point id",
    tags=["Data"],
)
def get_data_detail_by_datapoint(
    req: Request,
    datapoint_id: int,
    question_ids: Optional[List[int]] = Query(default=None),
    history: Optional[bool] = Query(default=False),
    session: Session = Depends(get_session),
):
    # get data
    data = crud_data.get_data_by_datapoint_id(
        session=session, datapoint_id=datapoint_id
    )
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    # get monitoring data for that datapoint
    monitoring_data = crud_data.get_monitoring_data(
        session=session, identifier=data.identifier
    )
    monitoring_data_ids = [md.id for md in monitoring_data]

    # get answers
    answers = session.query(Answer).filter(
        Answer.data.in_(monitoring_data_ids)
    )
    ra = crud_answer.get_answer_by_data(session=session, data=datapoint_id)
    rd = [
        {
            "question": r.question_detail.name
            if r.question_detail
            else r.question,
            "answer": r.options if r.options else r.text,
        }
        for r in ra
    ]
    if question_ids:
        answers = answers.filter(Answer.question.in_(question_ids))
    answers = answers.all()
    answers = [a.to_detail for a in answers]

    # get histories
    histories = None
    if history:
        histories = session.query(History).filter(
            History.data.in_(monitoring_data_ids)
        )
    if history and question_ids:
        histories = histories.filter(History.question.in_(question_ids))
    if history:
        histories = histories.all()
        histories = [h.to_monitoring for h in histories]
    if histories:
        answers = answers + histories

    return {
        "id": data.id,
        "name": data.name,
        "answers": answers,
        "registration_data": rd,
    }
