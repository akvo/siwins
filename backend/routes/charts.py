from collections import defaultdict
from fastapi import APIRouter, Query
from fastapi import Depends, Request
from itertools import groupby
from typing import List, Optional
from sqlalchemy.orm import Session
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
    get_jmp_config_by_form,
    get_jmp_labels
)


charts_route = APIRouter()


def group_children(data, labels):
    total = len(data)
    childs = []
    if not labels:
        categories = []
        category = groupby(data, key=lambda d: d["category"])
        for k, values in category:
            if k in categories:
                continue
            categories.append(k)
        labels = [{"name": c} for c in categories]
    groups = groupby(data, key=lambda d: d["administration"])
    counter = defaultdict()
    for k, values in groups:
        print(k)
        for v in list(values):
            if v["category"] in list(counter):
                counter[v["category"]] += 1
            else:
                counter[v["category"]] = 1
    for lb in labels:
        label = lb.get("name")
        count = counter[label] if label in counter else 0
        percent = count / total * 100 if count > 0 else 0
        childs.append(
            {
                "option": label,
                "count": count,
                "percent": percent,
                "color": lb.get("color"),
            }
        )
    print(childs)
    return {"administration": 'a', "score": 0, "child": childs}


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
    "/chart/jmp-data/{type:path}",
    name="charts:get_aggregated_jmp_chart_data",
    summary="get jmp chart aggregate data",
    tags=["Charts"],
)
def get_aggregated_jmp_chart_data(
    req: Request,
    type: str,
    # q: Optional[List[str]] = Query(None),
    session: Session = Depends(get_session),
):
    # options = check_query(q) if q else None
    data = get_jmp_overview(session=session, name=type)
    configs = get_jmp_config_by_form()
    labels = get_jmp_labels(configs=configs, name=type)
    group = group_children(data, labels)
    # return {"form": form_id, "question": type, "data": group}
