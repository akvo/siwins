from fastapi import APIRouter
from fastapi import Depends, Request

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.connection import get_session
from AkvoResponseGrouper.models import Category, GroupedCategory
from AkvoResponseGrouper.utils import (
    transform_categories_to_df,
    get_counted_category,
    group_by_category_output,
)
from db.crud_data import get_all_data


charts_route = APIRouter()


@charts_route.get(
    "/charts/bar",
    response_model=List[GroupedCategory],
    name="charts:get_bar_charts",
    summary="get data to show in bar charts",
    tags=["Charts"],
)
def get_bar_charts(
    req: Request,
    form: int,
    name: str,
    session: Session = Depends(get_session),
):
    all = get_all_data(session=session, current=True)
    lst = [a.serialize for a in all]
    ids = [i["id"] for i in lst]
    categories = (
        session.query(Category)
        .filter(
            and_(
                Category.form == form,
                Category.name == name,
                Category.data.in_(ids),
            )
        )
        .all()
    )
    categories = [c.serialize for c in categories]
    df = transform_categories_to_df(categories=categories)
    dt = get_counted_category(df=df)
    return group_by_category_output(data=dt)