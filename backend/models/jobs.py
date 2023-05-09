# Please don't use **kwargs
# Keep the code clean and CLEAR

import enum
from typing import Optional
from datetime import datetime
from typing_extensions import TypedDict
from pydantic import BaseModel
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import (
    Column, Integer, Text, DateTime
)
import sqlalchemy.dialects.postgresql as pg
from db.connection import Base


JOB_STATUS_TEXT = {
    0: "Pending",
    1: "in Progress",
    2: "Failed",
    3: "Done"
}


class JobStatus(enum.Enum):
    pending = 0
    in_progress = 1
    failed = 2
    done = 3


class JobsDict(TypedDict):
    id: int
    status: Optional[JobStatus] = JobStatus.pending
    payload: str
    info: Optional[dict] = None
    created: Optional[str] = None
    available: Optional[datetime] = None


class Jobs(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True, nullable=True)
    status = Column(Integer, nullable=True, default=0)
    payload = Column(Text)
    info = Column(MutableDict.as_mutable(pg.JSONB), nullable=True)
    created = Column(DateTime, default=datetime.utcnow)
    available = Column(DateTime, nullable=True)

    def __init__(
        self,
        payload: str,
        info: Optional[dict] = None,
        status: Optional[JobStatus] = None,
        available: Optional[datetime] = None
    ):
        self.info = info
        self.status = status
        self.payload = payload
        self.available = available

    def __repr__(self) -> int:
        return f"<Jobs {self.id}>"

    @property
    def serialize(self) -> JobsDict:
        return {
            "id": self.id,
            "status": self.status,
            "payload": self.payload,
            "info": self.info,
            "created": self.created.strftime("%B %d, %Y at %I:%M %p"),
            "available": self.available,
        }


class JobsBase(BaseModel):
    id: int
    status: Optional[JobStatus] = JobStatus.pending
    payload: str
    info: Optional[dict] = None
    created: Optional[str] = None
    available: Optional[datetime] = None

    class Config:
        orm_mode = True
