from math import ceil
from itertools import groupby
from http import HTTPStatus
from fastapi import Depends, Request
from fastapi import APIRouter, HTTPException, Query
from fastapi.security import HTTPBearer

# from fastapi.security import HTTPBasicCredentials as credentials
from typing import List, Optional
from sqlalchemy.orm import Session
from db.connection import get_session
from db.crud_data import (
    get_data, get_all_data, get_data_by_id,
    get_monitoring_data, get_history_data_by_school
)
from db.crud_province_view import (
    get_province_number_answer
)
from db.crud_jmp import (
    get_jmp_school_detail_popup
)
from models.data import MapsData, ChartDataDetail
from models.data import DataDetail, DataResponse
from models.answer import Answer
from models.history import History
from middleware import check_query, check_indicator_query
from source.main_config import (
    SchoolInformationEnum,
    CascadeLevels
)

security = HTTPBearer()
data_route = APIRouter()

school_information_cascade = CascadeLevels.school_information.value


@data_route.get(
    "/data",
    response_model=DataResponse,
    name="data:get_all",
    summary="get all data with pagination",
    tags=["Data"]
)
def get_paginated_data(
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
    res = get_data(
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
        None, description="format: [int, int]"),
    prov: Optional[List[str]] = Query(
        None, description="format: province name \
            (filter by province name)"),
    sctype: Optional[List[str]] = Query(
        None, description="format: school_type name \
            (filter by shcool type)")
    # credentials: credentials = Depends(security)
):
    # check indicator query
    answer_data_ids, answer_temp = check_indicator_query(
        session=session, indicator=indicator, number=number)
    # for advance filter and indicator option filter
    options = check_query(q) if q else None
    # get the data
    data = get_all_data(
        session=session,
        current=True,
        options=options,
        data_ids=answer_data_ids,
        prov=prov,
        sctype=sctype
    )
    # map answer by identifier for each datapoint
    data = [d.to_maps for d in data]
    for d in data:
        data_id = str(d.get('identifier'))
        d["answer"] = answer_temp.get(data_id) or {}
    return data


# current chart history detail (delete?)
@data_route.get(
    "/data/chart/{data_id}",
    response_model=ChartDataDetail,
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
    data = get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    # get monitoring data for that datapoint
    monitoring_data = get_monitoring_data(
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
    # serialize and update monitoring data
    res = data.to_chart_detail
    res["monitoring"] = monitoring
    return res


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
    # monitoring: Optional[bool] = Query(default=False),
    session: Session = Depends(get_session),
):
    province_lv = school_information_cascade.get(
        SchoolInformationEnum.province.value)
    school_name_lv = school_information_cascade.get(
        SchoolInformationEnum.school_name.value)
    school_code_lv = school_information_cascade.get(
        SchoolInformationEnum.school_code.value)
    # get data
    data = get_data_by_id(session=session, id=data_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    # get history data
    history_data = get_history_data_by_school(
        session=session,
        schools=data.school_information,
        year_conducted=data.year_conducted)
    # get JMP status
    jmp_levels = []
    histories = [data.get_data_id_and_year_conducted]
    histories += [hd.get_data_id_and_year_conducted for hd in history_data]
    for h in histories:
        jmp_check = get_jmp_school_detail_popup(
            session=session, data_id=h.get('id'))
        for lev in jmp_check:
            category = lev.get('category')
            level = lev.get('options')[0].get('name')
            jmp_levels.append({
                'year': h.get('year_conducted'),
                'history': h.get('history'),
                'category': category,
                'level': level
            })
    # start generate school detail popup
    data = data.to_school_detail_popup
    # province, school name - code
    school_information = data.get("school_information")
    current_province = school_information[province_lv]
    current_school_name = school_information[school_name_lv]
    current_school_code = school_information[school_code_lv]
    # sort answer by group / question order
    data["answer"] = sorted(
        data["answer"],
        key=lambda x: (x["qg_order"], x["q_order"])
    )
    # generate chart data for number answer
    number_qids = list(filter(
        lambda v: (v["type"] == "number"),
        data["answer"]
    ))
    number_qids = [v["question_id"] for v in number_qids]
    prov_numb_answers = get_province_number_answer(
        session=session,
        question_ids=number_qids,
        current=True)
    prov_numb_answers = [p.serialize for p in prov_numb_answers]
    for da in data["answer"]:
        del da["qg_order"]
        del da["q_order"]
        if da["type"] != "number":
            da["render"] = "value"
            continue
        # generate national data
        find_national_answers = list(filter(
            lambda x: (x["question"] == da["question_id"]),
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
            lambda x: (x["province"] == current_province),
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
    # group by question group
    groups = groupby(data["answer"], key=lambda d: d["question_group_id"])
    grouped_answer = []
    for k, values in groups:
        temp = list(values)
        qg_name = temp[0]["question_group_name"]
        child = [{
            "question_id": da["question_id"],
            "question_name": da["question_name"],
            "render": da["render"],
            "value": da["value"]
        } for da in temp]
        grouped_answer.append({
            "group": qg_name,
            "child": child
        })
    # Add JMP levels with history
    data["jmp_levels"] = jmp_levels
    data["answer"] = grouped_answer
    return data
