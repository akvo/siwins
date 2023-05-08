from http import HTTPStatus
from itertools import groupby
from fastapi import Depends, Request
from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db.connection import get_session
from models.question import QuestionType
from db.crud_data import (
    get_data_by_id, get_history_data_by_school
)
from db.crud_question import (
    get_question_by_id
)
from db.crud_answer import (
    get_answer_by_question,
    get_answer_by_data
)
from db.crud_province_view import (
    get_province_number_answer
)
from utils.functions import extract_school_information


security = HTTPBearer()
answer_route = APIRouter()


# Endpoint to fetch answer history
@answer_route.get(
    "/answer/history/{data_id:path}",
    name="answer:get_history",
    summary="get answer history by datapoint & question",
    tags=["Answer"]
)
def get_answer_history(
    req: Request,
    data_id: int,
    question_id: int,
    session: Session = Depends(get_session)
):
    # fetch current data
    data = get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Data not found"
        )
    # check question
    question = get_question_by_id(session=session, id=question_id)
    if not question:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Question not found"
        )
    if question.type != QuestionType.number:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Question not a number type"
        )
    # province, school name - code
    (
        current_province,
        current_school_type,
        current_school_name,
        current_school_code
    ) = extract_school_information(data.school_information)
    # get history data
    history_data = get_history_data_by_school(
        session=session,
        schools=data.school_information,
        year_conducted=data.year_conducted)
    # get answer histories
    history_answers = get_answer_by_question(
        session=session,
        question=question.id,
        data_ids=[h.id for h in history_data])
    history_answers = [
        ha.to_school_detail_popup for ha in history_answers]
    # generate chart data for number answer
    number_qids = [question.id]
    prov_numb_answers = get_province_number_answer(
        session=session,
        question_ids=number_qids,
        current=False)
    prov_numb_answers = [p.serialize for p in prov_numb_answers]
    for da in history_answers:
        del da["question_group_id"]
        del da["question_group_name"]
        del da["qg_order"]
        del da["q_order"]
        del da["attributes"]
        if da["type"] != "number":
            da["render"] = "value"
            continue
        # generate national data
        find_national_answers = list(filter(
            lambda x: (
                x["question"] == da[
                    "question_id"] and x[
                        "year_conducted"] == da["year"]
            ),
            prov_numb_answers
        ))
        national_value_sum = sum(
            [p["value"] for p in find_national_answers]
        )
        national_count_sum = sum(
            [p["count"] for p in find_national_answers]
        )
        # generate province data
        find_province_answers = list(filter(
            lambda x: (
                x["province"] == current_province and x[
                    "year_conducted"] == da["year"]
            ),
            find_national_answers
        ))
        prov_value_sum = sum(
            [p["value"] for p in find_province_answers]
        )
        prov_count_sum = sum(
            [p["count"] for p in find_province_answers]
        )
        temp_numb = [{
            "level": f"{current_school_name} - {current_school_code}",
            "total": da["value"],
            "count": 1
        }, {
            "level": current_province,
            "total": prov_value_sum,
            "count": prov_count_sum
        }, {
            "level": "National",
            "total": national_value_sum,
            "count": national_count_sum
        }]
        da["render"] = "chart"
        da["value"] = temp_numb
    # EOL generate chart data for number answer
    return history_answers


# Endpoint to fetch data answers
@answer_route.get(
    "/answer/data/{data_id:path}",
    name="answer:get_data_answers",
    summary="get data answers by data id",
    tags=["Answer"]
)
def get_data_answers_history(
    req: Request,
    data_id: int,
    session: Session = Depends(get_session)
):
    # fetch current data
    data = get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Data not found"
        )
    answers = get_answer_by_data(
        session=session, data=data_id)
    answers = [a.to_data_answer_detail for a in answers]
    answers.sort(key=lambda x: (x.get("qg_order"), x.get("q_order")))
    groups = groupby(answers, key=lambda d: d["question_group_id"])
    grouped_answer = []
    for k, values in groups:
        temp = list(values)
        qg_name = temp[0]["question_group_name"]
        child = [{
            "question_id": da["question_id"],
            "question_name": da["question_name"],
            "value": da["value"]
        } for da in temp]
        grouped_answer.append({
            "group": qg_name,
            "child": child
        })
    return grouped_answer
