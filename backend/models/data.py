# Please don't use **kwargs
# Keep the code clean and CLEAR

from datetime import datetime
from typing_extensions import TypedDict
from typing import Optional, List, Union
from pydantic import BaseModel, confloat
from sqlalchemy import (
    Column, Float, String, Boolean, Integer,
    ForeignKey, DateTime, BigInteger
)
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import relationship
from db.connection import Base
from models.answer import Answer, AnswerDict
from models.answer import (
    AnswerBase, MonitoringAnswerDict,
    AnswerDictWithText
)
from models.form import Form
from models.history import History
from models.question import (
    QuestionAttributes,
    QuestionType
)


class GeoData(BaseModel):
    long: confloat(ge=-180.0, le=180.0)
    lat: confloat(ge=-90, le=90)


class DataDict(TypedDict):
    id: int
    name: Optional[str] = None
    form: int
    registration: bool
    current: bool
    datapoint_id: Optional[int] = None
    identifier: Optional[str] = None
    geo: Optional[GeoData] = None
    year_conducted: Optional[int] = None
    school_information: Optional[List[str]] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    answer: List[AnswerDict]


class DataSimplified(TypedDict):
    id: int
    name: Optional[str] = None
    geo: Optional[GeoData] = None
    year_conducted: Optional[int] = None
    school_information: Optional[Union[List[str], dict]] = None


class DataResponse(BaseModel):
    current: int
    data: List[DataSimplified]
    total: int
    total_page: int


class MapsData(BaseModel):
    id: int
    identifier: str
    name: str
    school_information: dict
    year_conducted: int
    geo: List[float]
    answer: Union[AnswerDict, dict]


class RegistrationDict(TypedDict):
    question: str
    answer: Union[str, int, List[str]]


class DataDetail(BaseModel):
    id: int
    name: str
    year_conducted: int
    school_information: List[str]
    jmp_levels: List[dict]
    answer: List[dict]


class DataDetailPopup(BaseModel):
    id: int
    name: str
    year_conducted: int
    school_information: dict
    jmp_levels: List[dict]
    answer: List[dict]


class ChartDataDetail(TypedDict):
    id: int
    name: str
    registration: Optional[List[AnswerDictWithText]] = []
    monitoring: Optional[List[MonitoringAnswerDict]] = []


class Data(Base):
    __tablename__ = "data"
    id = Column(BigInteger, primary_key=True, index=True, nullable=True)
    datapoint_id = Column(BigInteger, ForeignKey("data.id"), nullable=True)
    identifier = Column(String, nullable=True)
    name = Column(String)
    form = Column(BigInteger, ForeignKey(Form.id))
    registration = Column(Boolean, default=True)
    geo = Column(pg.ARRAY(Float), nullable=True)
    year_conducted = Column(Integer, nullable=True)
    school_information = Column(pg.ARRAY(String), nullable=True)
    created = Column(DateTime, nullable=True)
    updated = Column(DateTime, nullable=True)
    current = Column(Boolean, default=False)
    answer = relationship(
        Answer,
        cascade="all, delete",
        passive_deletes=True,
        backref="answer",
        order_by=Answer.created.desc(),
    )
    history = relationship(
        History,
        cascade="all, delete",
        passive_deletes=True,
        backref="history",
        order_by=History.created.desc(),
    )
    monitoring = relationship("Data", remote_side=[id])

    def __init__(
        self,
        name: str,
        form: int,
        geo: List[float],
        updated: datetime,
        created: datetime,
        registration: bool,
        current: Optional[bool] = False,
        id: Optional[int] = None,
        identifier: Optional[str] = None,
        datapoint_id: Optional[int] = None,
        year_conducted: Optional[int] = None,
        school_information: Optional[List[str]] = None,
    ):
        self.id = id
        self.datapoint_id = datapoint_id
        self.identifier = identifier
        self.name = name
        self.form = form
        self.registration = registration
        self.current = current
        self.geo = geo
        self.year_conducted = year_conducted
        self.school_information = school_information
        self.updated = updated
        self.created = created

    def __repr__(self) -> int:
        return f"<Data {self.id}>"

    @property
    def serialize(self) -> DataDict:
        return {
            "id": self.id,
            "datapoint_id": self.datapoint_id,
            "identifier": self.identifier,
            "name": self.name,
            "form": self.form,
            "registration": self.registration,
            "current": self.current,
            "geo": {
                "lat": self.geo[0], "long": self.geo[1]
            } if self.geo else None,
            "year_conducted": self.year_conducted,
            "school_information": self.school_information,
            "created": self.created.strftime("%B %d, %Y"),
            "updated": self.updated.strftime(
                "%B %d, %Y"
            ) if self.updated else None,
            "answer": [a.formatted for a in self.answer],
            "history": [h.formatted for h in self.history],
        }

    @property
    def simplify(self) -> DataSimplified:
        return {
            "id": self.id,
            "name": self.name,
            "geo": {
                "lat": self.geo[0], "long": self.geo[1]
            } if self.geo else None,
            "year_conducted": self.year_conducted,
            "school_information": self.school_information
        }

    @property
    def to_maps(self) -> MapsData:
        return {
            "id": self.id,
            "identifier": self.identifier,
            "name": self.name,
            "school_information": self.school_information,
            "year_conducted": self.year_conducted,
            "geo": self.geo,
            "answer": {}
        }

    # only used in test case
    @property
    def to_monitoring_data(self) -> ChartDataDetail:
        answers = [a.to_monitoring for a in self.answer]
        histories = [h.to_monitoring for h in self.history]
        return {
            "id": self.id,
            "name": self.name,
            "registration": [a.formatted for a in self.answer],
            "monitoring": answers + histories,
        }

    @property
    def to_school_detail_popup(self) -> DataDetail:
        answer_filter = QuestionAttributes.school_detail_popup.value
        answers = [a.to_school_detail_popup for a in self.answer]
        answers = list(filter(
            lambda x: (
                (
                    x.get(
                        "attributes"
                    ) and answer_filter in x.get(
                        "attributes"
                    )
                ) or x.get(
                    "type"
                ) == QuestionType.photo.value
            ),
            answers
        ))
        return {
            "id": self.id,
            "name": self.name,
            "year_conducted": self.year_conducted,
            "school_information": self.school_information,
            "answer": answers
        }

    @property
    def to_chart_detail(self) -> ChartDataDetail:
        return {
            "id": self.id,
            "name": self.name,
            "registration": [
                a.formatted_with_question_text
                for a in self.answer
            ],
            "monitoring": [],
        }

    @property
    def get_data_id_and_year_conducted(self):
        return {
            "id": self.id,
            "history": not self.current,
            "year_conducted": self.year_conducted
        }


class DataBase(BaseModel):
    id: int
    name: str
    form: int
    registration: bool
    current: Optional[bool] = False
    datapoint_id: Optional[int] = None
    identifier: Optional[str] = None
    geo: Optional[GeoData] = None
    year_conducted: Optional[int] = None
    school_information: Optional[List[str]] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    answer: List[AnswerBase]

    class Config:
        orm_mode = True
