import collections
from itertools import groupby
from fastapi import APIRouter, Query
from fastapi import Depends, Request, HTTPException
from typing import List, Optional
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, aliased
from db.connection import get_session
from AkvoResponseGrouper.views import get_categories
from AkvoResponseGrouper.models import Category
from AkvoResponseGrouper.utils import (
    transform_categories_to_df,
    get_counted_category,
    group_by_category_output,
)
from db.crud_data import get_all_data, get_year_conducted_from_datapoint
from db.crud_jmp import (
    get_jmp_overview,
    get_jmp_config,
    get_jmp_labels,
    group_children,
)
from db.crud_cascade import get_province_of_school_information
from db.crud_option import get_option_by_question_id
from db.crud_question import get_question_by_id
from db.crud_province_view import (
    get_province_number_answer,
    get_province_option_answer,
)
from middleware import check_query, check_indicator_param
from models.answer import Answer
from models.question import QuestionType
from models.data import Data
from models.option import Option


charts_route = APIRouter()


@charts_route.get(
    "/chart/number_of_school",
    name="charts:get_number_of_school",
    summary="show total of current schools reported",
    tags=["Charts"],
)
def get_number_of_school(
    req: Request,
    session: Session = Depends(get_session),
):
    data = get_all_data(
        session=session, columns=[Data.id], current=True, count=True
    )
    return {"name": "Number of schools", "total": data}


@charts_route.get(
    "/chart/bar",
    response_model=List[dict],
    name="charts:get_bar_charts",
    summary="get data to show in bar charts",
    tags=["Charts"],
)
def get_bar_charts(
    req: Request,
    name: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
):
    configs = get_jmp_config()
    all_data = get_all_data(session=session, columns=[Data.id], current=True)
    ids = [d.id for d in all_data]
    filters = [Category.data.in_(ids)]
    if name:
        filters.append(func.lower(Category.name) == name.lower())
    categories = session.query(Category).filter(*filters).all()
    categories = [c.serialize for c in categories]
    df = transform_categories_to_df(categories=categories)
    dt = get_counted_category(df=df)
    res = group_by_category_output(data=dt)
    for r in res:
        labels = get_jmp_labels(configs=configs, name=r.get("category"))
        temp = []
        for o in r.get("options"):
            o["color"] = None
        for label in labels:
            find_count = next(
                (
                    x
                    for x in r.get("options")
                    if x["name"]
                    and x["name"].lower() == label.get("name").lower()
                ),
                None,
            )
            label["count"] = find_count.get("count") if find_count else 0
            temp.append(label)
        r["options"] = temp if labels else r["options"]
    return res


@charts_route.get(
    "/chart/national/{question:path}",
    name="charts:get_national_charts_by_question",
    summary="show national chart data by question",
    tags=["Charts"],
)
def get_national_chart_data_by_question(
    req: Request,
    question: int,
    session: Session = Depends(get_session),
):
    current_question = get_question_by_id(session=session, id=question)
    if not current_question:
        raise HTTPException(status_code=404, detail="Question not found")
    if current_question.type not in [
        QuestionType.number,
        QuestionType.option,
        QuestionType.multiple_option,
    ]:
        raise HTTPException(
            status_code=404, detail="Question type not supported"
        )
    qname = current_question.display_name or current_question.name
    if current_question.type == QuestionType.number:
        # get number national data
        res = get_province_number_answer(
            session=session, question_ids=[question], current=True
        )
        total = sum(r.value for r in res)
        count = sum(r.count for r in res)
        return {"name": qname, "total": total, "count": count}
    # get option national data
    options = get_option_by_question_id(session=session, question=question)
    options = [o.simplify for o in options]
    res = get_province_option_answer(
        session=session, question_ids=[question], current=True
    )
    res = [r.serialize for r in res]
    for opt in options:
        temps = list(
            filter(lambda x: (x["value"].lower() == opt["name"].lower()), res)
        )
        opt["count"] = sum(t["count"] for t in temps)
    return {"name": qname, "option": options}


@charts_route.get(
    "/chart/generic-bar/{question:path}",
    name="charts:get_generic_chart_data",
    summary="get generic bar chart aggregate data",
    tags=["Charts"],
)
def get_aggregated_chart_data(
    req: Request,
    question: int,
    history: Optional[bool] = False,
    session: Session = Depends(get_session),
    stack: Optional[int] = Query(
        None, description="question id to create stack BAR"
    ),
    indicator: int = Query(None, description="indicator is a question id"),
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
):
    current = not history
    # check indicator param
    indicator = check_indicator_param(
        session=session, indicator=indicator, number=number
    )
    # for advance filter and indicator option filter
    options = check_query(q) if q else None
    if question == stack:
        raise HTTPException(status_code=406, detail="Not Acceptable")
    # options values
    question_options = get_option_by_question_id(
        session=session, columns=[Option.id, Option.name], question=question
    )
    stack_options = []
    if stack:
        stack_options = get_option_by_question_id(
            session=session, columns=[Option.id, Option.name], question=stack
        )
    # year conducted
    year_conducted = get_year_conducted_from_datapoint(
        session=session, current=current
    )
    years = [
        {"year": y.year_conducted, "current": y.current}
        for y in year_conducted
    ]
    res = []
    # fetch data
    data_source = get_all_data(
        session=session,
        columns=[Data.id, Data.current, Data.year_conducted],
        current=None if history else current,
        year_conducted=(
            [y.year_conducted for y in year_conducted] if history else None
        ),
        options=options,
        prov=prov,
        sctype=sctype,
    )
    data_source = [
        {"id": d.id, "current": d.current, "year": d.year_conducted}
        for d in data_source
    ]
    # iterate over years conducted
    for y in years:
        year = y.get("year")
        current = y.get("current")
        data = list(
            filter(
                lambda c: (c["year"] == year and c["current"] == current),
                data_source,
            )
        )
        data = [d["id"] for d in data]
        # chart query
        type = "BAR"
        if stack:
            type = "BARSTACK"
            answerStack = aliased(Answer)
            answer = session.query(
                Answer.options, answerStack.options, func.count()
            )
            # filter
            answer = answer.filter(Answer.data.in_(data))
            answer = answer.join(
                (answerStack, Answer.data == answerStack.data)
            )
            answer = answer.filter(
                and_(
                    Answer.question == question, answerStack.question == stack
                )
            )
            answer = answer.group_by(Answer.options, answerStack.options)
            answer = answer.all()
            answer = [
                {
                    "axis": a[0][0].lower(),
                    "stack": a[1][0].lower(),
                    "value": a[2],
                }
                for a in answer
            ]
            temp = []
            answer.sort(key=lambda x: x["axis"])
            for k, v in groupby(answer, key=lambda x: x["axis"]):
                child = [{x["stack"]: x["value"]} for x in list(v)]
                counter = collections.Counter()
                for d in child:
                    counter.update(d)
                child = [
                    {"name": key, "value": val}
                    for key, val in dict(counter).items()
                ]
                temp.append({"group": k, "child": child})
            # remap result to options
            remap = []
            for qo in question_options:
                group = qo.name.lower()
                find_group = next(
                    (x for x in temp if x["group"] == group), None
                )
                fg_child = find_group["child"] if find_group else []
                child = []
                for so in stack_options:
                    name = so.name.lower()
                    find_child = next(
                        (x for x in fg_child if x["name"] == name), None
                    )
                    child.append(
                        {
                            "name": name,
                            "value": find_child["value"] if find_child else 0,
                        }
                    )
                remap.append(
                    {
                        "year": year,
                        "history": not current,
                        "group": group,
                        "child": child,
                    }
                )
            answer = remap
        else:
            answer = session.query(Answer.options, func.count(Answer.id))
            # filter
            answer = answer.filter(Answer.data.in_(data))
            answer = answer.filter(Answer.question == question)
            answer = answer.group_by(Answer.options)
            answer = answer.all()
            answer = [{a[0][0].lower(): a[1]} for a in answer]
            counter = collections.Counter()
            for d in answer:
                counter.update(d)
            temp = [{"name": k, "value": v} for k, v in dict(counter).items()]
            # remap result to options
            remap = []
            for qo in question_options:
                name = qo.name.lower()
                find_temp = next((x for x in temp if x["name"] == name), None)
                remap.append(
                    {
                        "year": year,
                        "history": not current,
                        "name": name,
                        "value": find_temp["value"] if find_temp else 0,
                    }
                )
            answer = remap
        res += answer
    return {"type": type, "data": res}


@charts_route.get(
    "/chart/jmp-data/{type:path}",
    name="charts:get_aggregated_jmp_chart_data",
    summary="get jmp chart aggregate data",
    tags=["Charts"],
)
def get_aggregated_jmp_chart_data(
    req: Request,
    type: str,
    history: Optional[bool] = False,
    session: Session = Depends(get_session),
    indicator: int = Query(None, description="indicator is a question id"),
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
):
    current = not history
    # check indicator param
    indicator = check_indicator_param(
        session=session, indicator=indicator, number=number
    )
    # for advance filter and indicator option filter
    options = check_query(q) if q else None
    # administration / province
    parent_administration = get_province_of_school_information(session=session)
    parent_administration = [p.simplify for p in parent_administration]
    for p in parent_administration:
        p["children"] = [p["name"]]
    # year conducted
    year_conducted = get_year_conducted_from_datapoint(
        session=session, current=current
    )
    years = [
        {"year": y.year_conducted, "current": y.current}
        for y in year_conducted
    ]
    # get from data table
    data = get_all_data(
        session=session,
        columns=[
            Data.id,
            Data.school_information,
            Data.year_conducted,
            Data.current,
        ],
        current=None if history else current,
        year_conducted=(
            [y.year_conducted for y in year_conducted] if history else None
        ),
        options=options,
        prov=prov,
        sctype=sctype,
    )
    # get categories from akvo response grouper by data_ids
    try:
        data_ids = [d.id for d in data]
        categories = get_categories(session=session, name=type, data=data_ids)
    except Exception:
        categories = []
    # generate JMP data
    data = get_jmp_overview(session=session, categories=categories, data=data)
    configs = get_jmp_config()
    labels = get_jmp_labels(configs=configs, name=type)
    group_by_year = []
    for y in years:
        group = list(
            map(
                lambda p: group_children(p, data, labels, y),
                parent_administration,
            )
        )
        group_by_year += group
    return {"question": type, "data": group_by_year}
