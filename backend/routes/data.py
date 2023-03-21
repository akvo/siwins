from math import ceil
from http import HTTPStatus
from fastapi import Depends, Request
from fastapi import APIRouter, HTTPException, Query
from fastapi.security import HTTPBearer

# from fastapi.security import HTTPBasicCredentials as credentials
from typing import List, Optional
from sqlalchemy.orm import Session
from db import crud_data, crud_answer, crud_question
from db.connection import get_session
from models.data import MapsData, MonitoringData
from models.data import DataDetail, DataResponse
from models.answer import Answer
from models.history import History
from models.question import QuestionType
from middleware import check_query

security = HTTPBearer()
data_route = APIRouter()


@data_route.get(
    "/data",
    response_model=DataResponse,
    name="data:get_all",
    summary="get all data with pagination",
    tags=["Data"]
)
def get_data(
    req: Request,
    page: int = 1,
    perpage: int = 10,
    form_id: int = Query(None),
    session: Session = Depends(get_session)
):
    # TODO:: How we handle registration monitoring form data ?
    # if we do the pagination like this, the data will contains
    # mix of registration and monitoring data
    # I think better if we wait for the design
    # for now only show registration data
    res = crud_data.get_data(
        session=session,
        registration=True,
        skip=(perpage * (page - 1)),
        perpage=perpage)
    count = res.get("count")
    if not count:
        return []
    total_page = ceil(count / perpage) if count > 0 else 0
    if total_page < page:
        return []
    data = [d.serialize for d in res.get("data")]
    return {
        "current": page,
        "data": data,
        "total": count,
        "total_page": total_page,
    }


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
    indicator: int = Query(
        None, description="indicator is a question id"),
    q: Optional[List[str]] = Query(
        None, description="format: question_id|option value \
            (indicator option & advance filter)"),
    number: Optional[List[int]] = Query(
        None, description="format: [int, int]"
    )
    # credentials: credentials = Depends(security)
):
    # 1. indicator filter by option,
    #  - use same format as advanced filter: q param = qid|option
    # 2. indicator filter by number,
    #  - check if indicator qtype is number
    #  - filter answers by number param
    question = crud_question.get_question_by_id(
        session=session, id=indicator)
    is_number = question.type == QuestionType.number \
        if question else False
    if number and not is_number:
        raise HTTPException(
            status_code=400,
            detail="Bad Request, indicator is not number type")
    if number and len(number) != 2:
        raise HTTPException(
            status_code=400,
            detail="Bad Request, number param length must equal to 2")
    # get all answers by indicator
    answer_data_ids = None
    answer_temp = {}
    if indicator:
        answers = crud_answer.get_answer_by_question(
            session=session,
            question=indicator,
            number=number)
        answer_data_ids = [a.data for a in answers]
        answers = [
            a.formatted_with_data for a in answers
        ] if answers else []
        for a in answers:
            key = a.get('identifier')
            del a['data']
            del a['identifier']
            answer_temp.update({key: a})
    # for advance filter and indicator option filter
    options = check_query(q) if q else None
    # get the data
    data = crud_data.get_all_data(
        session=session,
        registration=True,
        options=options,
        data_ids=answer_data_ids
    )
    # map answer by identifier for each datapoint
    data = [d.to_maps for d in data]
    for d in data:
        data_id = str(d.get('identifier'))
        d["answer"] = answer_temp.get(data_id) or {}
    return data


@data_route.get(
    "/data/chart/{data_id}",
    response_model=MonitoringData,
    name="data:get_chart_data",
    summary="get monitoring data for chart",
    tags=["Data"],
)
def get_data_detail_for_chart(
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
    "/data/{data_id}",
    response_model=DataDetail,
    name="data:get_data_detail",
    summary="get data detail by data id",
    tags=["Data"],
)
def get_data_detail_by_data_id(
    req: Request,
    data_id: int,
    monitoring: Optional[bool] = Query(default=False),
    session: Session = Depends(get_session),
):
    # get data
    data = crud_data.get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    return data.to_detail
