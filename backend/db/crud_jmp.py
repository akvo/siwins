import json
from collections import defaultdict
from itertools import groupby
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

# from AkvoResponseGrouper.views import get_categories
from AkvoResponseGrouper.models import Category
from AkvoResponseGrouper.utils import (
    transform_categories_to_df,
    get_counted_category,
    group_by_category_output,
)
from models.data import Data

from source.main import main_config

SchoolInformationEnum = main_config.SchoolInformationEnum
CascadeLevels = main_config.CascadeLevels
ResponseGrouperCustomConfig = main_config.ResponseGrouperCustomConfig


province_enum = SchoolInformationEnum.province.value
province_level = CascadeLevels.school_information.value[province_enum]


def group_children(p, data_source, labels, year_conducted):
    # filter by administration and year
    year = year_conducted.get("year")
    data = list(
        filter(
            lambda d: (
                d["administration"] in p["children"] and d["year"] == year
            ),
            data_source,
        )
    )
    current = year_conducted.get("current") or False
    data = [
        {
            "category": d["category"] if "category" in d else None,
            "data": d["data"],
        }
        for d in data
    ]
    # counter
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
    # if no labels defined in category.json
    if not labels:
        labels = list(set([x["category"] for x in data]))
        labels.sort()
        labels = [{"name": x, "color": None, "order": 0} for x in labels]
    # end of labels
    for lb in labels:
        label = lb["name"]
        count = counter[label] if label in counter else 0
        percent = round(count / total * 100, 2) if count > 0 else 0
        childs.append(
            {
                "option": label,
                "count": count,
                "percent": percent,
                "color": lb.get("color") or None,
                "order": lb.get("order") or None,
            }
        )
    return {
        "year": year,
        "history": not current,
        "administration": p["name"],
        "score": 0,
        "child": childs,
    }


# def get_jmp_table_view(session: Session, data: list, configs: list):
#     ids = [str(d["id"]) for d in data]
#     dts = ",".join(ids)
#     try:
#         gc = get_categories(session=session, data=dts)
#     except Exception:
#         gc = []
#     for d in data:
#         cs = list(filter(lambda c: (c["data"] == d["id"]), gc))
#         categories = []
#         for c in cs:
#             labels = get_jmp_labels(configs=configs, name=c["name"])
#             fl = list(filter(
#                 lambda l: l["name"].lower() == str(c["category"]).lower(),
#                 labels,
#             ))
#             color = None
#             if len(fl):
#                 color = fl[0]["color"]
#             categories.append(
#                 {
#                     "key": c["name"].lower(),
#                     "value": c["category"],
#                     "color": color,
#                 }
#             )
#         d.update({"categories": categories})
#     return data


def get_jmp_overview(
    session: Session, categories: List[dict], data: List[Data]
):
    data = [
        {
            "data": d.id,
            "administration": d.school_information[province_level],
            "year": d.year_conducted,
            "current": d.current,
        }
        for d in data
    ]
    try:
        for d in data:
            fc = list(filter(lambda c: (c["data"] == d["data"]), categories))
            if len(fc):
                d.update(fc[0])
        return data
    except Exception:
        return data


def get_jmp_config():
    try:
        with open("./.category.json", "r") as categories:
            json_config = json.load(categories)
    except Exception:
        json_config = []
    # generate name_id from category name
    for jc in json_config:
        # add custom name
        name = jc.get("name")
        # ** Use JMP display name instead of name
        # ** (to change all JMP naming on routes)
        # name = jc["display_name"] if "display_name" in jc else jc["name"]
        name_id = name.split(" ")
        name_id = "_".join(name_id).lower()
        jc["name_id"] = name_id
        # add question group
        custom_config = ResponseGrouperCustomConfig[name_id].value
        jc["question_group"] = custom_config.get("question_group") or None
        jc["category_type"] = custom_config.get("category_type") or None
    configs = json_config
    return configs


def get_jmp_labels(configs: list, name: str) -> list:
    fl = list(filter(lambda val: val["name"].lower() == name.lower(), configs))
    labels = []
    if len(fl):
        try:
            labels = fl[0]["labels"]
        except KeyError:
            return []
    return labels


def get_jmp_school_detail_popup(
    session: Session,
    data_ids: List[int],
    name: Optional[str] = None,
    raw: Optional[bool] = False,
) -> List[Category]:
    categories = session.query(Category).filter(Category.data.in_(data_ids))
    if name:
        categories = categories.filter(
            func.lower(Category.name) == name.lower()
        )
    categories = categories.all()
    categories = [c.serialize for c in categories]
    if raw:
        return categories
    df = transform_categories_to_df(categories=categories)
    dt = get_counted_category(df=df)
    return group_by_category_output(data=dt)
