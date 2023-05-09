# import aiofiles
from datetime import datetime
from xlrd import open_workbook, XLRDError
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import (
    Depends, Request, APIRouter, Query,
    HTTPException, BackgroundTasks
)
from fastapi.security import HTTPBearer
from db.connection import get_session
from db.crud_form import get_form_name
from db.crud_question import get_question_name
# from utils import excel, storage
from utils.helper import UUID
from db.crud_jobs import add_jobs
from models.jobs import JobsBase
from middleware import check_query
from source.main_config import LOG_PATH


out_file_path = "./tmp/"
ftype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

security = HTTPBearer()
file_route = APIRouter()


def test_excel(file):
    try:
        open_workbook(file)
        # return storage.upload(file, "test")
        return True
    except XLRDError:
        raise HTTPException(status_code=404, detail="Not Valid Excel File")


def test(job: dict):
    today = datetime.today().strftime("%y%m%d")
    log_file = f"download_log_{today}.txt"
    with open(f"{LOG_PATH}/{log_file}", mode="a+") as log:
        log.write(f"job_id: {job['id']} || {str(job)}")


@file_route.get(
    "/download/data",
    response_model=JobsBase,
    summary="request to download data",
    name="excel-data:generate",
    tags=["File"])
async def generate_file(
    req: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    monitoring_round: int = Query(
        None, description="filter data by monitoring round (year)"),
    q: Optional[List[str]] = Query(
        None, description="format: question_id|option value \
            (indicator option & advance filter)"),
    prov: Optional[List[str]] = Query(
        None, description="format: province name \
            (filter by province name)"),
    sctype: Optional[List[str]] = Query(
        None, description="format: school_type name \
            (filter by shcool type)"),
):
    tags = []
    options = check_query(q) if q else None
    form_name = get_form_name(session=session)
    form_name = form_name.replace(" ", "_").lower()
    today = datetime.today().strftime("%y%m%d")
    out_file = UUID(f"{form_name}-{today}").str
    if monitoring_round:
        tags.append({
            "q": "Monitoring round",
            "o": monitoring_round
        })
    if q:
        qids = [o.split("|")[0] for o in q]
        question_names = get_question_name(
            session=session, ids=qids
        )
        for o in q:
            [qid, option] = o.split("|")
            question = question_names.get(qid) or ""
            tags.append({"q": question, "o": option})
    if prov:
        tags.append({
            "q": "Province",
            "o": ", ".join(prov)
        })
    if sctype:
        tags.append({
            "q": "School type",
            "o": ", ".join(sctype)
        })
    res = add_jobs(
        session=session,
        payload=f"download-{out_file}.xlsx",
        info={
            "form_name": form_name,
            "monitoring_round": monitoring_round,
            "options": options,
            "province": prov,
            "school_type": sctype,
            "tags": tags
        })
    background_tasks.add_task(test, res)
    return res
