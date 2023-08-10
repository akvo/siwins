# Please don't use **kwargs
# Keep the code clean and CLEAR

import json
from datetime import datetime
from typing_extensions import TypedDict
from typing import Optional, List, Union
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, Text, String, BigInteger
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship
import sqlalchemy.dialects.postgresql as pg
from db.connection import Base
from models.question import QuestionType


# util
def append_value(self, answer):
    type = self.question_detail.type
    if type in [QuestionType.number]:
        answer.update({"value": self.value})
    if type in [QuestionType.text, QuestionType.geo, QuestionType.date]:
        answer.update({"value": self.text})
    if type == QuestionType.option:
        answer.update({"value": self.options[0]})
    if type == QuestionType.multiple_option:
        answer.update({"value": self.options})
    if type == QuestionType.photo:
        obj = json.loads(self.text)
        answer.update({"value": obj.get('filename')})
    if type == QuestionType.geoshape:
        answer.update({"value": json.loads(self.text)})
    if type == QuestionType.cascade:
        answer.update({"value": self.options})
    return answer


class AnswerDict(TypedDict):
    question: int
    value: Union[
        int, float, str, bool, dict, List[str], List[int], List[float], None
    ]


class AnswerDictWithText(TypedDict):
    question_id: int
    question: str
    type: QuestionType
    value: Union[
        int, float, str, bool, dict, List[str], List[int], List[float], None
    ]


class DataAnswerDetailDict(TypedDict):
    qg_order: int
    question_group_id: str
    question_group_name: str
    question_id: int
    q_order: int
    question_name: str
    type: QuestionType
    value: Union[
        int, float, str, bool, dict, List[str], List[int], List[float], None
    ]


class SchoolPopupAnswerDict(TypedDict):
    qg_order: int
    question_group_id: str
    question_group_name: str
    question_id: int
    q_order: int
    question_name: str
    type: str
    attributes: List[str]
    value: Union[
        int, float, str, bool, dict, List[str], List[int], List[float], None
    ]
    history: bool
    year: int


class MonitoringAnswerDict(TypedDict):
    question_id: int
    question: str
    type: str
    value: Union[
        int, float, str, bool, dict, List[str], List[int], List[float], None
    ]
    date: str
    history: bool


class Answer(Base):
    __tablename__ = "answer"
    id = Column(Integer, primary_key=True, index=True, nullable=True)
    question = Column(
        BigInteger,
        ForeignKey("question.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    data = Column(
        BigInteger,
        ForeignKey("data.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    text = Column(Text, nullable=True)
    value = Column(Float, nullable=True)
    options = Column(pg.ARRAY(String), nullable=True)
    created = Column(DateTime, nullable=True)
    updated = Column(DateTime, nullable=True)
    question_detail = relationship("Question", backref="answer")

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
        return f"<Answer {self.id}>"

    @property
    def serialize(self) -> AnswerDict:
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
    def formatted(self) -> AnswerDict:
        answer = {
            "question": self.question,
        }
        answer = append_value(self, answer)
        return answer

    @property
    def formatted_with_question_text(self) -> AnswerDictWithText:
        answer = {
            "question_id": self.question,
            "question": self.question_detail.name,
            "type": self.question_detail.type.value
        }
        answer = append_value(self, answer)
        return answer

    @property
    def to_monitoring(self) -> MonitoringAnswerDict:
        answer = {
            "history": False,
            "question_id": self.question,
            "question": self.question_detail.name,
            "date": self.created.strftime("%b %d, %Y - %-I:%M:%-S %p"),
            "type": self.question_detail.type.value,
        }
        answer = append_value(self, answer)
        return answer

    @property
    def to_data_answer_detail(self) -> DataAnswerDetailDict:
        qdetail = self.question_detail
        answer = {
            "qg_order": qdetail.question.order,
            "question_group_id": qdetail.question.id,
            "question_group_name": qdetail.question.name,
            "question_id": self.question,
            "q_order": qdetail.order,
            "question_name": qdetail.name,
            "type": qdetail.type.value,
            "personal_data": qdetail.personal_data
        }
        answer = append_value(self, answer)
        return answer

    @property
    def to_school_detail_popup(self) -> SchoolPopupAnswerDict:
        qdetail = self.question_detail
        qg_name = qdetail.question.display_name or qdetail.question.name
        answer = {
            "qg_order": qdetail.question.order,
            "question_group_id": qdetail.question.id,
            "question_group_name": qg_name,
            "question_id": self.question,
            "q_order": qdetail.order,
            "question_name": qdetail.display_name or qdetail.name,
            "type": qdetail.type.value,
            "attributes": qdetail.attributes,
            "history": not self.answer.current,
            "year": self.answer.year_conducted
        }
        answer = append_value(self, answer)
        return answer

    @property
    def formatted_with_data(self) -> AnswerDict:
        answer = {
            "data": self.data,
            "identifier": self.answer.identifier,
            "question": self.question,
        }
        answer = append_value(self, answer)
        return answer


class AnswerBase(BaseModel):
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
