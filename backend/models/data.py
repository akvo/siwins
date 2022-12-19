# Please don't use **kwargs
# Keep the code clean and CLEAR

from datetime import datetime
from typing_extensions import TypedDict
from typing import Optional, List
from pydantic import BaseModel
from pydantic import confloat
from sqlalchemy import Column, Float, String, Boolean
from sqlalchemy import ForeignKey, DateTime, BigInteger
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import relationship
from db.connection import Base
from models.answer import Answer, AnswerDict
from models.answer import AnswerBase, MonitoringAnswerDict
from models.form import Form
from models.history import History


class GeoData(BaseModel):
    long: confloat(ge=-180.0, le=180.0)
    lat: confloat(ge=-90, le=90)


class DataDict(TypedDict):
    id: int
    name: str
    form: int
    registration: bool
    datapoint_id: Optional[int] = None
    identifier: Optional[str] = None
    geo: Optional[GeoData] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    answer: List[AnswerDict]


class DataResponse(BaseModel):
    current: int
    data: List[DataDict]
    total: int
    total_page: int


class MapsData(BaseModel):
    id: int
    name: str
    geo: List[float]


class MonitoringData(TypedDict):
    id: int
    name: str
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
    created = Column(DateTime, nullable=True)
    updated = Column(DateTime, nullable=True)
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
        id: Optional[int] = None,
        identifier: Optional[str] = None,
        datapoint_id: Optional[int] = None,
    ):
        self.id = id
        self.datapoint_id = datapoint_id
        self.identifier = identifier
        self.name = name
        self.form = form
        self.registration = registration
        self.geo = geo
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
            "geo": {"lat": self.geo[0], "long": self.geo[1]}
            if self.geo
            else None,
            "created": self.created.strftime("%B %d, %Y"),
            "updated": self.updated.strftime("%B %d, %Y")
            if self.updated
            else None,
            "answer": [a.formatted for a in self.answer],
        }

    @property
    def to_maps(self) -> MapsData:
        return {
            "id": self.id,
            "name": self.name,
            "geo": self.geo,
        }

    @property
    def to_monitoring_data(self) -> MonitoringData:
        answers = [a.to_monitoring for a in self.answer]
        histories = [h.to_monitoring for h in self.history]
        return {
            "id": self.id,
            "name": self.name,
            "monitoring": answers + histories,
        }


class DataBase(BaseModel):
    id: int
    name: str
    form: int
    registration: bool
    datapoint_id: Optional[int] = None
    identifier: Optional[str] = None
    geo: Optional[GeoData] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    answer: List[AnswerBase]

    class Config:
        orm_mode = True
