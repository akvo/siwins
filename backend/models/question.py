# Please don't use **kwargs
# Keep the code clean and CLEAR

import enum
from typing import Optional, List
from typing_extensions import TypedDict
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, BigInteger
from sqlalchemy import Boolean, Integer, String, Enum
from sqlalchemy.orm import relationship
import sqlalchemy.dialects.postgresql as pg
from db.connection import Base
from models.option import OptionBase


class QuestionType(enum.Enum):
    text = "text"
    number = "number"
    option = "option"
    multiple_option = "multiple_option"
    photo = "photo"
    date = "date"
    geo = "geo"
    cascade = "cascade"
    geoshape = "geoshape"


class DependencyDict(TypedDict):
    id: int
    options: List[str]


class QuestionDict(TypedDict):
    id: int
    form: int
    question_group: int
    order: Optional[int] = None
    name: str
    meta: bool
    meta_geo: bool
    type: QuestionType
    required: bool
    option: Optional[List[OptionBase]] = None
    dependency: Optional[List[dict]] = None


class Question(Base):
    __tablename__ = "question"
    id = Column(BigInteger, primary_key=True, index=True, nullable=True)
    form = Column(BigInteger, ForeignKey("form.id"))
    question_group = Column(BigInteger, ForeignKey("question_group.id"))
    name = Column(String)
    order = Column(Integer, nullable=True)
    meta = Column(Boolean, default=False)
    meta_geo = Column(Boolean, default=False)
    type = Column(Enum(QuestionType), default=QuestionType.text)
    required = Column(Boolean, nullable=True)
    dependency = Column(pg.ARRAY(pg.JSONB), nullable=True)

    option = relationship(
        "Option", cascade="all, delete", passive_deletes=True, backref="option"
    )

    def __init__(
        self,
        id: Optional[int],
        name: str,
        order: int,
        form: int,
        question_group: int,
        meta: bool,
        meta_geo: bool,
        type: QuestionType,
        required: Optional[bool],
        dependency: Optional[List[dict]],
    ):
        self.id = id
        self.form = form
        self.order = order
        self.question_group = question_group
        self.name = name
        self.meta = meta
        self.meta_geo = meta_geo
        self.type = type
        self.required = required
        self.dependency = dependency

    def __repr__(self) -> int:
        return f"<Question {self.id}>"

    @property
    def serialize(self) -> QuestionDict:
        return {
            "id": self.id,
            "form": self.form,
            "question_group": self.question_group,
            "name": self.name,
            "order": self.order,
            "meta": self.meta,
            "meta_geo": self.meta_geo,
            "type": self.type,
            "required": self.required,
            "dependency": self.dependency,
            "option": self.option,
        }


class QuestionBase(BaseModel):
    id: int
    form: int
    question_group: int
    name: str
    order: Optional[int] = None
    meta: bool
    meta_geo: bool
    type: QuestionType
    required: bool
    option: List[OptionBase]
    dependency: Optional[List[dict]]

    class Config:
        orm_mode = True


class QuestionIds(BaseModel):
    id: int
