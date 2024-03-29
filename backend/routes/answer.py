from http import HTTPStatus
from typing import Optional
from itertools import groupby
from fastapi import Depends, Request
from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db.connection import get_session
from models.question import QuestionType
from db.crud_data import get_data_by_id, get_history_data_by_school
from db.crud_question import get_question_by_id
from db.crud_answer import get_answer_by_question, get_answer_by_data
from db.crud_province_view import get_province_number_answer
from utils.functions import extract_school_information
from utils.helper import MathOperation
from source.main import main_config

QuestionConfig = main_config.QuestionConfig


security = HTTPBearer()
answer_route = APIRouter()


# Endpoint to fetch answer history
@answer_route.get(
    "/answer/history/{data_id:path}",
    name="answer:get_history",
    summary="get answer history by datapoint & question",
    tags=["Answer"],
)
def get_answer_history(
    req: Request,
    data_id: int,
    question_id: int,
    aggregate: Optional[MathOperation] = MathOperation.average,
    session: Session = Depends(get_session),
):
    # fetch current data
    data = get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    # check question
    question = get_question_by_id(session=session, id=question_id)
    if not question:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Question not found"
        )
    if question.type != QuestionType.number:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Question not a number type",
        )
    # province, school name - code
    (
        current_province,
        current_school_type,
        current_school_name,
        current_school_code,
    ) = extract_school_information(data.school_information)
    # get history data
    history_data = get_history_data_by_school(
        session=session,
        schools=data.school_information,
        year_conducted=data.year_conducted,
    )
    # get answer histories
    history_answers = get_answer_by_question(
        session=session,
        question=question.id,
        data_ids=[h.id for h in history_data],
    )
    history_answers = [ha.to_school_detail_popup for ha in history_answers]
    # generate chart data for number answer
    number_qids = [question.id]
    prov_numb_answers = get_province_number_answer(
        session=session, question_ids=number_qids, current=False
    )
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
        find_national_answers = list(
            filter(
                lambda x: (
                    x["question"] == da["question_id"]
                    and x["year_conducted"] == da["year"]
                ),
                prov_numb_answers,
            )
        )
        national_value_sum = sum([p["value"] for p in find_national_answers])
        national_count_sum = sum([p["count"] for p in find_national_answers])
        national_value_avg = (
            national_value_sum / national_count_sum
            if national_count_sum
            else 0
        )
        # generate province data
        find_province_answers = list(
            filter(
                lambda x: (
                    x["province"] == current_province
                    and x["year_conducted"] == da["year"]
                ),
                find_national_answers,
            )
        )
        prov_value_sum = sum([p["value"] for p in find_province_answers])
        prov_count_sum = sum([p["count"] for p in find_province_answers])
        prov_value_avg = (
            prov_value_sum / prov_count_sum if prov_count_sum else 0
        )
        # provide value by aggregate param
        national_value = round(national_value_avg, 2)
        prov_value = round(prov_value_avg, 2)
        if aggregate.value == MathOperation.sum.value:
            national_value = national_value_sum
            prov_value = prov_value_sum
        # eol provide value by aggregate param
        temp_numb = [
            {
                "level": f"{current_school_name} - {current_school_code}",
                "total": da["value"],
                "count": 1,
                "value": da["value"],
            },
            {
                "level": current_province,
                "total": prov_value_sum,
                "count": prov_count_sum,
                "value": prov_value,
            },
            {
                "level": "National",
                "total": national_value_sum,
                "count": national_count_sum,
                "value": national_value,
            },
        ]
        da["render"] = "chart"
        da["value"] = temp_numb
    # EOL generate chart data for number answer
    return history_answers


# Endpoint to fetch data answers
@answer_route.get(
    "/answer/data/{data_id:path}",
    name="answer:get_data_answers",
    summary="get data answers by data id",
    tags=["Answer"],
)
def get_data_answer_detail(
    req: Request, data_id: int, session: Session = Depends(get_session)
):
    # fetch current data
    data = get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    answers = get_answer_by_data(session=session, data=data_id)
    answers = [a.to_data_answer_detail for a in answers]
    answers.sort(key=lambda x: (x.get("qg_order"), x.get("q_order")))
    groups = groupby(answers, key=lambda d: d["question_group_id"])
    grouped_answer = []
    for k, values in groups:
        temp = list(values)
        qg_name = temp[0]["question_group_name"]
        child = []
        for da in temp:
            qid = da["question_id"]
            qname = da["question_name"]
            qtype = da["type"]
            value = da["value"]
            # don't include PII answer
            personal_data = da["personal_data"]
            if personal_data:
                continue
            if qid == QuestionConfig.school_information.value:
                qtype = "school_information"
                value = extract_school_information(
                    school_information=da["value"], to_object=True
                )
            if qtype == QuestionType.multiple_option.value:
                value = ", ".join(value)
            child.append(
                {
                    "question_id": qid,
                    "question_name": qname,
                    "value": value,
                    "type": qtype,
                }
            )
        grouped_answer.append({"group": qg_name, "child": child})
    return grouped_answer
