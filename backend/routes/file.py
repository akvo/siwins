# import aiofiles
from datetime import datetime
from xlrd import open_workbook, XLRDError
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import Depends, Request, APIRouter, Query, HTTPException
from fastapi.security import HTTPBearer
from db.connection import get_session
# from db.crud_form import get_form_name
# from db.crud_question import get_question_name
# from utils import excel, storage
from utils.helper import UUID
from db.crud_jobs import add_jobs
from models.jobs import JobsBase
from middleware import check_query


def test_excel(file):
    try:
        open_workbook(file)
        # return storage.upload(file, "test")
        return True
    except XLRDError:
        raise HTTPException(status_code=404, detail="Not Valid Excel File")


out_file_path = "./tmp/"
security = HTTPBearer()
file_route = APIRouter()
ftype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


@file_route.get(
    "/download/data",
    response_model=JobsBase,
    summary="request to download data",
    name="excel-data:generate",
    tags=["File"])
async def generate(
    req: Request,
    session: Session = Depends(get_session),
    q: Optional[List[str]] = Query(None)
):
    tags = []
    options = check_query(q) if q else None
    # form_name = get_form_name(session=session, id=form_id)
    form_name = "Test"
    form_name = form_name.replace(" ", "_").lower()
    today = datetime.today().strftime("%y%m%d")
    out_file = UUID(f"{form_name}-{today}").str
    if q:
        for o in q:
            [qid, option] = o.split("|")
            # question = get_question_name(session=session, id=qid)
            tags.append({"q": qid, "o": option})
    res = add_jobs(
        session=session,
        payload=f"download-{out_file}.xlsx",
        info={
            "form_name": form_name,
            "options": options,
            "tags": tags
        })
    return res
