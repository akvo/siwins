import os
import pandas as pd
from sqlalchemy import desc
from sqlalchemy.orm import Session
from db.crud_data import get_all_data
from db.crud_question import get_excel_headers
from models.data_answer import DataAnswer
from utils.helper import HText
from models.data import Data


def rearange_columns(col_names: list):
    col_question = list(filter(lambda x: HText(x).hasnum, col_names))
    col_names = [
        "id", "identifier", "created_at", "datapoint_name", "geolocation"
    ] + col_question
    return col_names


def generate_download_data(session: Session, jobs: dict, file: str):
    info = jobs.get("info") or {}
    if os.path.exists(file):
        os.remove(file)
    province_name = "All Administration Level"
    if info.get("province"):
        province_name = info.get("province") or []
        province_name = ", ".join(province_name)
    filtered_data = get_all_data(
        session=session,
        columns=[Data.id],
        monitoring_round=info.get("monitoring_round"),
        options=info.get("options"),
        prov=info.get("province"),
        sctype=info.get("school_type"),
        data_ids=info.get("data_ids"),
    )
    filtered_data_ids = [d.id for d in filtered_data]
    # fetch data from data answer view
    data = session.query(DataAnswer).filter(
        DataAnswer.id.in_(filtered_data_ids)
    ).order_by(desc(DataAnswer.created)).all()
    data = [d.to_data_frame for d in data]
    # generate file
    df = pd.DataFrame(data)
    questions = get_excel_headers(session=session)
    for q in questions:
        if q not in list(df):
            df[q] = ""
    col_names = rearange_columns(questions)
    df = df[col_names]
    # rename columns, remove question id
    df = df.rename(columns=(
        lambda col: col.split("|")[1].strip()
        if "|" in col else col
    ))
    # eol remove question id
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='data', index=False)
    context = [{
        "context": "Form Name",
        "value": info["form_name"]
    }, {
        "context": "Download Date",
        "value": jobs["created"]
    }, {
        "context": "Province",
        "value": province_name
    }]
    for inf in info["tags"]:
        context.append({
            "context": "Filters",
            "value": f"{inf['q']} : {inf['o']}"
        })
    context = pd.DataFrame(context).groupby(
        ["context", "value"], sort=False).first()
    context.to_excel(writer, sheet_name='context', startrow=0, header=False)
    workbook = writer.book
    worksheet = writer.sheets['context']
    format = workbook.add_format({
        'align': 'left',
        'bold': False,
        'border': 0,
    })
    worksheet.set_column('A:A', 20, format)
    worksheet.set_column('B:B', 30, format)
    merge_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#45add9',
        'color': '#ffffff',
    })
    worksheet.merge_range('A1:B1', 'Context', merge_format)
    writer.save()
    return file, context
