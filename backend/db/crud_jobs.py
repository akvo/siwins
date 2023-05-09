from typing import Optional
from typing_extensions import TypedDict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.jobs import Jobs, JobsBase, JobStatus


def add_jobs(
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


def update_jobs(
    session: Session,
    id: int,
    payload: Optional[str] = None,
    status: int = None,
    info: Optional[TypedDict] = None
) -> JobsBase:
    jobs = session.query(Jobs).filter(Jobs.id == id).first()
    if payload:
        jobs.payload = payload
    if status:
        jobs.status = status
    if status == JobStatus.done.value:
        jobs.available = datetime.now()
    if info:
        jobs.info = info
    session.commit()
    session.flush()
    session.refresh(jobs)
    return jobs.serialize


def query_jobs(
    session: Session,
    status: Optional[int] = None,
    limit: Optional[int] = 5,
    skip: Optional[int] = 0
) -> JobsBase:
    jobs = session.query(Jobs)
    if status:
        jobs = jobs.filter(Jobs.status == status)
    jobs = jobs.order_by(
        desc(Jobs.created)
    ).offset(skip).limit(limit).all()
    return [j.serialize for j in jobs]
