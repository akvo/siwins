import collections
from collections import defaultdict
from fastapi import APIRouter, Query
from fastapi import Depends, Request, HTTPException
from itertools import groupby
from typing import List, Optional
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, aliased
from db.connection import get_session
from AkvoResponseGrouper.models import Category, GroupedCategory
from AkvoResponseGrouper.utils import (
    transform_categories_to_df,
    get_counted_category,
    group_by_category_output,
)
from db.crud_data import get_all_data
from db.crud_jmp import (
    get_jmp_overview,
    get_jmp_config,
    get_jmp_labels
)
from db.crud_cascade import get_province_of_school_information
from middleware import check_query, check_indicator_query
from models.answer import Answer


charts_route = APIRouter()


def group_children(p, data_source, labels):
    data = list(
        filter(lambda d: (d["administration"] in p["children"]), data_source)
    )
    data = [{
        "category": d["category"] if "category" in d else None,
        "data": d["data"]
    }for d in data]
    # if no labels defined in category.json
    if not labels:
        labels = list(set([x['category'] for x in data]))
        labels.sort()
        labels = [{'name': x, 'color': None} for x in labels]
    total = len(data)
    childs = []
    groups = groupby(data, key=lambda d: d["category"])
    counter = defaultdict()
    for k, values in groups:
        for v in list(values):
            if v["category"] in list(counter):
                counter[v["category"]] += 1
            else:
                counter[v["category"]] = 1
    for lb in labels:
        label = lb["name"]
        count = counter[label] if label in counter else 0
        percent = round(count / total * 100, 2) if count > 0 else 0
        childs.append(
            {
                "option": label,
                "count": count,
                "percent": percent,
                "color": lb["color"],
            }
        )
    return {"administration": p["name"], "score": 0, "child": childs}


@charts_route.get(
    "/charts/bar",
    response_model=List[GroupedCategory],
    name="charts:get_bar_charts",
    summary="get data to show in bar charts",
    tags=["Charts"],
)
def get_bar_charts(
    req: Request,
    name: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
):
    all = get_all_data(session=session, current=True)
    lst = [a.serialize for a in all]
    ids = [i["id"] for i in lst]
    filters = [Category.data.in_(ids)]
    if name:
        filters.append(Category.name == name)
    categories = session.query(Category).filter(*filters).all()
    categories = [c.serialize for c in categories]
    df = transform_categories_to_df(categories=categories)
    dt = get_counted_category(df=df)
    return group_by_category_output(data=dt)


@charts_route.get(
    "/chart/generic-bar/{question:path}",
    name="charts:get_generic_chart_data",
    summary="get generic bar chart aggregate data",
    tags=["Charts"]
)
def get_aggregated_chart_data(
    req: Request,
    question: int,
    session: Session = Depends(get_session),
    stack: Optional[int] = Query(
        None, description="question id to create stack BAR"),
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
):
    # check indicator query
    answer_data_ids, answer_temp = check_indicator_query(
        session=session, indicator=indicator, number=number)
    # for advance filter and indicator option filter
    options = check_query(q) if q else None
    if question == stack:
        raise HTTPException(status_code=406, detail="Not Acceptable")
    data = get_all_data(
        session=session,
        current=True,
        options=options,
        data_ids=answer_data_ids,
        prov=prov,
        sctype=sctype
    )
    data = [d.id for d in data]
    # chart query
    type = "BAR"
    if stack:
        type = "BARSTACK"
        answerStack = aliased(Answer)
        answer = session.query(
            Answer.options, answerStack.options, func.count())
        # filter
        answer = answer.filter(Answer.data.in_(data))
        answer = answer.join((answerStack, Answer.data == answerStack.data))
        answer = answer.filter(
            and_(Answer.question == question, answerStack.question == stack))
        answer = answer.group_by(Answer.options, answerStack.options)
        answer = answer.all()
        answer = [{
            "axis": a[0][0].lower(),
            "stack": a[1][0].lower(),
            "value": a[2]
        } for a in answer]
        temp = []
        answer.sort(key=lambda x: x["axis"])
        for k, v in groupby(answer, key=lambda x: x["axis"]):
            child = [{x["stack"]: x["value"]} for x in list(v)]
            counter = collections.Counter()
            for d in child:
                counter.update(d)
            child = [{
                "name": key,
                "value": val
            } for key, val in dict(counter).items()]
            temp.append({"group": k, "child": child})
        answer = temp
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
        answer = [{"name": k, "value": v} for k, v in dict(counter).items()]
    return {"type": type, "data": answer}


@charts_route.get(
    "/chart/jmp-data/{type:path}",
    name="charts:get_aggregated_jmp_chart_data",
    summary="get jmp chart aggregate data",
    tags=["Charts"],
)
def get_aggregated_jmp_chart_data(
    req: Request,
    type: str,
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
):
    # check indicator query
    answer_data_ids, answer_temp = check_indicator_query(
        session=session, indicator=indicator, number=number)
    # for advance filter and indicator option filter
    options = check_query(q) if q else None
    # generate JMP data
    parent_administration = get_province_of_school_information(
        session=session)
    parent_administration = [p.simplify for p in parent_administration]
    for p in parent_administration:
        p['children'] = [p['name']]
    data = get_jmp_overview(
        session=session,
        name=type,
        options=options,
        data_ids=answer_data_ids,
        prov=prov,
        sctype=sctype
    )
    configs = get_jmp_config()
    labels = get_jmp_labels(configs=configs, name=type)
    group = list(
        map(
            lambda p: group_children(p, data, labels),
            parent_administration,
        )
    )
    return {"question": type, "data": group}
