import os
import pandas as pd
from sqlalchemy import desc
from sqlalchemy.orm import Session
from db.crud_data import get_all_data
from db.crud_question import get_excel_headers
from db.crud_jmp import get_jmp_config
from models.data_answer import DataAnswer
from utils.helper import HText
from models.data import Data
from typing import Optional
from AkvoResponseGrouper.models import Category
from AkvoResponseGrouper.utils import transform_categories_to_df


def rearange_columns(
    col_names: list, computed_column_names: Optional[list] = []
):
    col_question = list(filter(lambda x: HText(x).hasnum, col_names))
    columns = (
        ["id", "identifier", "created_at", "datapoint_name", "geolocation"]
        + computed_column_names
        + col_question
    )
    return columns


def generate_download_data(session: Session, jobs: dict, file: str):
    info = jobs.get("info") or {}
    if os.path.exists(file):
        os.remove(file)
    province_name = "All Administration Level"
    if info.get("province"):
        province_name = info.get("province") or []
        province_name = ", ".join(province_name)
    # jmp configs
    configs = get_jmp_config()
    # ** Use JMP display name instead of name
    computed_column_names = [
        cf["display_name"] if "display_name" in cf else cf["name"]
        for cf in configs
    ]
    # query data
    monitoring_round = info.get("monitoring_round")
    filtered_data = get_all_data(
        session=session,
        columns=[Data.id],
        year_conducted=[monitoring_round] if monitoring_round else None,
        options=info.get("options"),
        prov=info.get("province"),
        sctype=info.get("school_type"),
        data_ids=info.get("data_ids"),
    )
    filtered_data_ids = [d.id for d in filtered_data]
    # fetch ar-category view
    computed_data = (
        session.query(Category)
        .filter(Category.data.in_(filtered_data_ids))
        .all()
    )
    computed_data = [cd.serialize for cd in computed_data]
    computed_data_df = transform_categories_to_df(categories=computed_data)
    # fetch data from data answer view
    data = (
        session.query(DataAnswer)
        .filter(DataAnswer.id.in_(filtered_data_ids))
        .order_by(desc(DataAnswer.created))
        .all()
    )
    data = [d.to_data_frame for d in data]
    # remap data with computed values
    for d in data:
        for ccn in configs:
            name = ccn["name"]
            display_name = (
                ccn["display_name"] if "display_name" in ccn else name
            )
            find_computed_value = computed_data_df[
                (computed_data_df["data"] == d["id"])
                & (computed_data_df["name"] == name)
            ]
            category = "-"
            if not find_computed_value.empty:
                category = find_computed_value["category"].iloc[0]
            d[display_name] = category
    # generate file
    df = pd.DataFrame(data)
    questions = get_excel_headers(session=session)
    for q in questions:
        if q not in list(df):
            df[q] = ""
    col_names = rearange_columns(
        col_names=questions, computed_column_names=computed_column_names
    )
    df = df[col_names]
    # rename columns, remove question id
    df = df.rename(
        columns=(lambda col: col.split("|")[1].strip() if "|" in col else col)
    )
    # Drop the 'id' column
    df = df.drop(columns=["id"])
    # eol remove question id
    writer = pd.ExcelWriter(file, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="data", index=False)
    context = [
        {"context": "Form Name", "value": info["form_name"]},
        {"context": "Download Date", "value": jobs["created"]},
        {"context": "Province", "value": province_name},
    ]
    for inf in info["tags"]:
        context.append(
            {"context": "Filters", "value": f"{inf['q']} : {inf['o']}"}
        )
    context = (
        pd.DataFrame(context).groupby(["context", "value"], sort=False).first()
    )
    context.to_excel(writer, sheet_name="context", startrow=0, header=False)
    workbook = writer.book
    worksheet = writer.sheets["context"]
    format = workbook.add_format(
        {
            "align": "left",
            "bold": False,
            "border": 0,
        }
    )
    worksheet.set_column("A:A", 20, format)
    worksheet.set_column("B:B", 30, format)
    merge_format = workbook.add_format(
        {
            "bold": True,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "#45add9",
            "color": "#ffffff",
        }
    )
    worksheet.merge_range("A1:B1", "Context", merge_format)
    writer.save()
    return file, context
