# from fastapi import HTTPException
from typing import Optional, Union
from typing_extensions import TypedDict
from datetime import datetime
from sqlalchemy.orm import Session
# from sqlalchemy import asc, desc
from models.jobs import Jobs, JobsBase, JobStatus


def add_job(
    session: Session,
    payload: str,
    info: Optional[TypedDict] = None
) -> JobsBase:
    jobs = Jobs(payload=payload, info=info)
    session.add(jobs)
    session.commit()
    session.flush()
    session.refresh(jobs)
    return jobs.serialize


def update_job(
    session: Session,
    id: int,
    payload: Optional[str] = None,
    status: Union[JobStatus] = None,
    info: Optional[TypedDict] = None
) -> JobsBase:
    jobs = session.query(Jobs).filter(Jobs.id == id).first()
    if payload:
        jobs.payload = payload
    if status:
        jobs.status = status
    if status == JobStatus.done:
        jobs.available = datetime.now()
    if info:
        jobs.info = info
    session.commit()
    session.flush()
    session.refresh(jobs)
    return jobs.serialize
