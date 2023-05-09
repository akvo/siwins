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
from fastapi.responses import FileResponse
from db.connection import get_session
from db.crud_form import get_form_name
from db.crud_question import get_question_name
from utils.storage import StorageFolder, upload, download
from utils.helper import UUID, write_log
from utils.downloader import generate_download_data
from db.crud_jobs import add_jobs, update_jobs, query_jobs
from models.jobs import JobsBase, JobStatus, JOB_STATUS_TEXT
from middleware import check_query
from source.main_config import DOWNLOAD_PATH


out_file_path = "./tmp/"
ftype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

security = HTTPBearer()
file_route = APIRouter()


def test_excel(file):
    try:
        open_workbook(file)
        return upload(file, "test")
        return True
    except XLRDError:
        raise HTTPException(status_code=404, detail="Not Valid Excel File")


def run_download(session: Session, jobs: dict):
    status = jobs.get("status")
    payload = jobs["payload"]
    # download start
    out_file = payload
    file, context = generate_download_data(
        session=session, jobs=jobs, file=f"{DOWNLOAD_PATH}/{out_file}")
    if file:
        output = upload(file, StorageFolder.download.value, out_file)
        status = JobStatus.done.value
        payload = output.split("/")[1]
    else:
        status = JobStatus.failed.value
    jobs = update_jobs(
        session=session,
        id=jobs.get("id"),
        payload=payload,
        status=status)
    # write download log
    job_id = f"job_id: {jobs['id']}"
    job_status = f"status: {JOB_STATUS_TEXT.get(status)}"
    log_content = f"{job_status} || {job_id} || {str(jobs)}"
    write_log(log_filename="download_log", log_content=log_content)


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
    background_tasks.add_task(run_download, session, res)
    return res


@file_route.get(
    "/download/file/{filename:path}",
    summary="download file by filename",
    name="excel-data:download",
    tags=["File"])
async def download_file(
    req: Request,
    filename: str,
    session: Session = Depends(get_session)
):
    filepath = download(f"{StorageFolder.download.value}/{filename}")
    return FileResponse(path=filepath, filename=filename, media_type=ftype)


@file_route.get(
    "/download/list",
    response_model=List[JobsBase],
    summary="list of generated dowload data",
    name="excel-data:download-list",
    tags=["File"])
async def download_list(
    req: Request,
    page: Optional[int] = 1,
    perpage: Optional[int] = 5,
    session: Session = Depends(get_session)
):
    res = query_jobs(
        session=session,
        limit=perpage,
        skip=(perpage * (page - 1))
    )
    if not res:
        raise HTTPException(status_code=404, detail="Not found")
    return res
