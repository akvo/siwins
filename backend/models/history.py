# Please don't use **kwargs
# Keep the code clean and CLEAR

from datetime import datetime
from typing_extensions import TypedDict
from typing import Optional, List, Union
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, Text, String, BigInteger
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship
import sqlalchemy.dialects.postgresql as pg
from db.connection import Base
from models.answer import append_value


class HistoryDict(TypedDict):
    question: int
    value: Union[
        int, float, str, bool, List[str], List[int], List[float], None
    ]


class MonitoringHistoryDict(TypedDict):
    question_id: int
    question: str
    type: str
    value: Union[
        int, float, str, bool, dict, List[str], List[int], List[float], None
    ]
    date: str
    history: bool


class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True, nullable=True)
    question = Column(BigInteger, ForeignKey("question.id"))
    data = Column(BigInteger, ForeignKey("data.id"))
    text = Column(Text, nullable=True)
    value = Column(Float, nullable=True)
    options = Column(pg.ARRAY(String), nullable=True)
    created = Column(DateTime, nullable=True)
    updated = Column(DateTime, nullable=True)
    question_detail = relationship("Question", foreign_keys=[question])

    def __init__(
        self,
        question: int,
        created: datetime,
        data: Optional[int] = None,
        text: Optional[str] = None,
        value: Optional[float] = None,
        options: Optional[List[str]] = None,
        updated: Optional[datetime] = None,
    ):
        self.question = question
        self.data = data
        self.text = text
        self.value = value
        self.options = options
        self.updated = updated
        self.created = created

    def __repr__(self) -> int:
        return f"<History {self.id}>"

    @property
    def serialize(self) -> HistoryDict:
        return {
            "id": self.id,
            "question": self.question,
            "data": self.data,
            "text": self.text,
            "value": self.value,
            "options": self.options,
            "created": self.created,
            "updated": self.updated,
        }

    @property
    def to_monitoring(self) -> MonitoringHistoryDict:
        answer = {
            "history": True,
            "question_id": self.question,
            "question": self.question_detail.name,
            "date": self.created.strftime("%b %d, %Y - %-I:%M:%-S %p"),
            "type": self.question_detail.type.value,
        }
        answer = append_value(self, answer)
        return answer


class HistoryBase(BaseModel):
    id: int
    question: int
    data: int
    text: Optional[str] = None
    value: Optional[float] = None
    options: Optional[List[str]] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    class Config:
        orm_mode = True
