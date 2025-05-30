import orjson
from math import ceil
from itertools import groupby
from http import HTTPStatus
from fastapi import Depends, Request, APIRouter, HTTPException, Query, Response
from fastapi.security import HTTPBearer

# from fastapi.security import HTTPBasicCredentials as credentials
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from db.connection import get_session
from db.crud_data import (
    get_all_data,
    get_data_by_id,
    get_monitoring_data,
    get_history_data_by_school,
)
from db.crud_province_view import get_province_number_answer
from db.crud_jmp import (
    get_jmp_school_detail_popup,
    get_jmp_config,
    get_jmp_labels,
)
from AkvoResponseGrouper.utils import (
    transform_categories_to_df,
    get_counted_category,
    group_by_category_output,
)
from models.data import (
    MapDataResponse,
    ChartDataDetail,
    DataDetailPopup,
    DataResponse,
    InitMapDataResponse,
)
from models.answer import Answer
from models.question import QuestionType
from models.history import History
from middleware import (
    check_query,
    check_indicator_query,
    check_jmp_query,
    check_indicator_param,
)
from utils.functions import extract_school_information
from utils.helper import MathOperation
from source.main import main_config

security = HTTPBearer()
data_route = APIRouter()


CURRENT_MONITORING_ROUND = main_config.MONITORING_ROUND


@data_route.get(
    "/data",
    response_model=DataResponse,
    name="data:get_all",
    summary="get all data with pagination",
    tags=["Data"],
)
def get_paginated_data(
    req: Request,
    page: int = 1,
    perpage: int = 10,
    monitoring_round: int = Query(
        None, description="filter data by monitoring round (year)"
    ),
    q: Optional[List[str]] = Query(
        None,
        description="format: question_id|option value \
            (indicator option & advance filter)",
    ),
    prov: Optional[List[str]] = Query(
        None,
        description="format: province name \
            (filter by province name)",
    ),
    sctype: Optional[List[str]] = Query(
        None,
        description="format: school_type name \
            (filter by shcool type)",
    ),
    session: Session = Depends(get_session),
):
    # check query
    options = check_query(q) if q else None
    res = get_all_data(
        session=session,
        year_conducted=[monitoring_round] if monitoring_round else None,
        options=options,
        prov=prov,
        sctype=sctype,
        skip=(perpage * (page - 1)),
        perpage=perpage,
    )
    count = res.get("count")
    if not count:
        return {
            "current": page,
            "data": [],
            "total": count,
            "total_page": 0,
        }
    total_page = ceil(count / perpage) if count > 0 else 0
    if total_page < page:
        return {
            "current": page,
            "data": [],
            "total": count,
            "total_page": total_page,
        }
    data = [d.simplify for d in res.get("data")]
    for d in data:
        d["school_information"] = extract_school_information(
            school_information=d.get("school_information"), to_object=True
        )
    return {
        "current": page,
        "data": data,
        "total": count,
        "total_page": total_page,
    }


@data_route.get(
    "/data/maps-init",
    response_model=InitMapDataResponse,
    name="data:init_maps_data",
    summary="get initial maps data",
    tags=["Data"],
)
def get_maps_init(
    req: Request,
    page: int = 1,
    perpage: int = 100,
    page_only: Optional[bool] = False,
    session: Session = Depends(get_session),
):
    # get the data
    page_data = get_all_data(
        session=session,
        # current=True,
        skip=(perpage * (page - 1)),
        perpage=perpage,
        year_conducted=[CURRENT_MONITORING_ROUND]
    )
    # handle pagination
    count = page_data.get("count")
    if not count:
        return {
            "current": page,
            "data": [],
            "total": count,
            "total_page": 0,
        }
    total_page = ceil(count / perpage) if count > 0 else 0
    if total_page < page:
        return {
            "current": page,
            "data": [],
            "total": count,
            "total_page": total_page,
        }
    if page_only:
        return {
            "current": page,
            "data": [],
            "total": count,
            "total_page": total_page,
        }
    # data
    data = page_data.get("data") or []
    data = [d.init_maps for d in data]
    # transform data
    for d in data:
        d["school_information"] = extract_school_information(
            school_information=d["school_information"], to_object=True
        )
    res = {
        "current": page,
        "data": data,
        "total": count,
        "total_page": total_page,
    }
    return Response(content=orjson.dumps(res), media_type="application/json")


@data_route.get(
    "/data/maps",
    response_model=MapDataResponse,
    name="data:get_maps_data",
    summary="get maps data",
    tags=["Data"],
)
def get_maps(
    req: Request,
    page: int = 1,
    perpage: int = 100,
    page_only: Optional[bool] = False,
    indicator: Union[int, str] = Query(
        None, description="indicator is a question id or JMP category"
    ),
    q: Optional[List[str]] = Query(
        None,
        description="format: question_id|option value \
            (indicator option & advance filter)",
    ),
    number: Optional[List[int]] = Query(
        None, description="format: [int, int]"
    ),
    prov: Optional[List[str]] = Query(
        None,
        description="format: province name \
            (filter by province name)",
    ),
    sctype: Optional[List[str]] = Query(
        None,
        description="format: school_type name \
            (filter by shcool type)",
    ),
    session: Session = Depends(get_session),
    # credentials: credentials = Depends(security)
):
    # check indicator param
    if "jmp" not in str(indicator):
        indicator = check_indicator_param(
            session=session, indicator=indicator, number=number
        )
    # jmp option/levek filter
    jmp_query, non_jmp_query = check_jmp_query(q)
    # for advance filter and indicator option filter
    options = check_query(non_jmp_query) if non_jmp_query else None
    # get the data
    page_data = get_all_data(
        session=session,
        current=True,
        options=options,
        prov=prov,
        sctype=sctype,
        skip=(perpage * (page - 1)),
        perpage=perpage,
    )
    # handle pagination
    count = page_data.get("count")
    if not count:
        return {
            "current": page,
            "data": [],
            "total": count,
            "total_page": 0,
        }
    total_page = ceil(count / perpage) if count > 0 else 0
    if total_page < page:
        return {
            "current": page,
            "data": [],
            "total": count,
            "total_page": total_page,
        }
    if page_only:
        return {
            "current": page,
            "data": [],
            "total": count,
            "total_page": total_page,
        }
    # data
    data = page_data.get("data") or []
    data_ids = [d.id for d in data]
    # indicator query
    answer_data_ids = []
    answer_temp = {}
    if "jmp" not in str(indicator):
        answer_data_ids, answer_temp = check_indicator_query(
            session=session,
            indicator=indicator,
            number=number,
            data_ids=data_ids,
        )
    # map answer by identifier for each datapoint
    data = [d.to_maps for d in data]
    jmp_name = None
    if "jmp" in str(indicator):
        # get JMP status
        jmp_name = indicator.split("-")[1]
        if "_" in jmp_name:
            jmp_name = jmp_name.split("_")
            jmp_name = " ".join(jmp_name)
        jmp_levels = get_jmp_school_detail_popup(
            session=session, data_ids=data_ids, name=jmp_name, raw=True
        )
    # filter data by answer_data_ids
    if indicator and "jmp" not in str(indicator):
        data = list(filter(lambda x: (x.get("id") in answer_data_ids), data))
    # transform data
    for d in data:
        # TODO:: DELETE commented code
        # d["school_information"] = extract_school_information(
        #     school_information=d["school_information"], to_object=True)
        d["jmp_filter"] = None
        data_id = str(d.get("identifier"))
        if "jmp" not in str(indicator):
            d["answer"] = answer_temp.get(data_id) or None
        if "jmp" in str(indicator):
            # JMP indicator answer
            find_jmp = next(
                (x for x in jmp_levels if x["data"] == d["id"]), None
            )
            if not find_jmp:
                continue
            df = transform_categories_to_df(categories=[find_jmp])
            dt = get_counted_category(df=df)
            jmp_res = group_by_category_output(data=dt)
            level = jmp_res[0].get("options")[0].get("name")
            d["jmp_filter"] = f"{jmp_name}|{level}"
            d["answer"] = level
    # JMP filter: filter data by jmp filter value in jmp_query
    if "jmp" in str(indicator) and jmp_query:
        data = list(
            filter(
                lambda x: (
                    x["jmp_filter"] and x["jmp_filter"].lower() in jmp_query
                ),
                data,
            )
        )
    for d in data:
        # delete jmp filter param
        if "jmp_filter" not in d:
            continue
        del d["jmp_filter"]
        del d["identifier"]
    res = {
        "current": page,
        "data": data,
        "total": count,
        "total_page": total_page,
    }
    return Response(content=orjson.dumps(res), media_type="application/json")


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
    response_model=DataDetailPopup,
    name="data:get_data_detail",
    summary="get data detail by data id",
    tags=["Data"],
)
def get_data_detail_popup_by_data_id(
    req: Request,
    data_id: int,
    aggregate: Optional[MathOperation] = MathOperation.average,
    session: Session = Depends(get_session),
):
    # get data
    data = get_data_by_id(session=session, id=data_id)
    current = data.current
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Data not found"
        )
    # get history data for JMP calculation
    history_data = get_history_data_by_school(
        session=session,
        schools=data.school_information,
        year_conducted=data.year_conducted,
    )
    # get JMP status
    configs = get_jmp_config()
    # jmp category
    category_type_jmp = list(
        filter(lambda x: x["category_type"] == "jmp", configs)
    )
    category_type_jmp = [c["name"].lower() for c in category_type_jmp]
    #
    jmp_levels = []
    histories = [data.get_data_id_and_year_conducted]
    histories += [hd.get_data_id_and_year_conducted for hd in history_data]
    for h in histories:
        jmp_check = get_jmp_school_detail_popup(
            session=session, data_ids=[h.get("id")]
        )
        for lev in jmp_check:
            category = lev.get("category")
            # skip if response grouper not in JMP category
            if category.lower() not in category_type_jmp:
                continue
            level = lev.get("options")[0].get("name")
            labels = get_jmp_labels(configs=configs, name=category)
            find_label = next(
                (
                    x
                    for x in labels
                    if level and x["name"].lower() == level.lower()
                ),
                None,
            )
            color = find_label.get("color") if find_label else None
            jmp_levels.append(
                {
                    "year": h.get("year_conducted"),
                    "history": h.get("history"),
                    "category": category,
                    "level": level,
                    "color": color,
                }
            )
    # start generate school detail popup
    data = data.to_school_detail_popup
    # province, school name - code
    (
        current_province,
        current_school_type,
        current_school_name,
        current_school_code,
    ) = extract_school_information(data.get("school_information"))
    # sort answer by group / question order
    data["answer"] = sorted(
        data["answer"], key=lambda x: (x["qg_order"], x["q_order"])
    )
    # generate chart data for number answer
    number_qids = list(
        filter(lambda v: (v["type"] == "number"), data["answer"])
    )
    number_qids = [v["question_id"] for v in number_qids]
    prov_numb_answers = get_province_number_answer(
        session=session, question_ids=number_qids, current=current
    )
    prov_numb_answers = [p.serialize for p in prov_numb_answers]
    for da in data["answer"]:
        del da["attributes"]
        if da["type"] == QuestionType.photo.value:
            # handle photo question to be one group
            da["qg_order"] = 0
            da["q_order"] = 0
            da["question_group_id"] = 0
            da["question_group_name"] = "Images"
            da["render"] = "image"
            continue
        if da["type"] == QuestionType.multiple_option.value:
            da["render"] = "value"
            da["value"] = ", ".join(da["value"])
            continue
        if da["type"] != QuestionType.number.value:
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
    # order and group by question group
    data["answer"].sort(key=lambda x: (x.get("qg_order"), x.get("q_order")))
    groups = groupby(data["answer"], key=lambda d: d["question_group_id"])
    grouped_answer = []
    for k, values in groups:
        temp = list(values)
        qg_name = temp[0]["question_group_name"]
        child = [
            {
                "question_id": da["question_id"],
                "question_name": da["question_name"],
                "render": da["render"],
                "history": da["history"],
                "year": da["year"],
                "value": da["value"],
            }
            for da in temp
        ]
        grouped_answer.append({"group": qg_name, "child": child})
    # Add JMP levels with history
    data["school_information"] = extract_school_information(
        school_information=data.get("school_information"), to_object=True
    )
    data["jmp_levels"] = jmp_levels
    data["answer"] = grouped_answer
    return data
