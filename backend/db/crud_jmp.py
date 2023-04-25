import json
from typing import List, Optional
from sqlalchemy.orm import Session
from AkvoResponseGrouper.views import get_categories
from db.crud_data import get_all_data


def get_jmp_table_view(session: Session, data: list, configs: list):
    ids = [str(d["id"]) for d in data]
    dts = ",".join(ids)
    try:
        gc = get_categories(session=session, data=dts)
    except Exception:
        gc = []
    for d in data:
        cs = list(filter(lambda c: (c["data"] == d["id"]), gc))
        categories = []
        for c in cs:
            labels = get_jmp_labels(configs=configs, name=c["name"])
            fl = list(
                filter(
                    lambda l: l["name"].lower() == str(c["category"]).lower(),
                    labels,
                )
            )
            color = None
            if len(fl):
                color = fl[0]["color"]
            categories.append(
                {
                    "key": c["name"].lower(),
                    "value": c["category"],
                    "color": color,
                }
            )
        d.update({"categories": categories})
    return data


def get_jmp_overview(
    session: Session,
    name: str,
    options: Optional[List[str]] = None,
    data_ids: Optional[List[int]] = None,
    prov: Optional[List[str]] = None,
    sctype: Optional[List[str]] = None
):
    data = get_all_data(
        session=session,
        current=True,
        options=options,
        data_ids=data_ids,
        prov=prov,
        sctype=sctype)
    data = [{
        "data": d.id,
        "administration": d.school_information[0],
        "geo": d.geo
    } for d in data]
    try:
        gc = get_categories(session=session, name=name)
        for d in data:
            fc = list(filter(lambda c: (c["data"] == d["data"]), gc))
            if len(fc):
                d.update(fc[0])
        return data
    except Exception:
        return data


def get_jmp_config() -> list:
    try:
        with open("./.category.json", "r") as categories:
            json_config = json.load(categories)
    except Exception:
        json_config = []
    configs = json_config
    return configs


def get_jmp_labels(configs: list, name: str) -> list:
    fl = list(filter(lambda l: l["name"].lower() == name.lower(), configs))
    labels = []
    if len(fl):
        try:
            labels = fl[0]["labels"]
        except KeyError:
            return []
    return labels
