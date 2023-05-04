# Please don't use **kwargs
# Keep the code clean and CLEAR

import enum
from typing import Optional, List, Union
from typing_extensions import TypedDict
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, BigInteger
from sqlalchemy import Boolean, Integer, String, Enum
from sqlalchemy.orm import relationship
import sqlalchemy.dialects.postgresql as pg
from db.connection import Base
from models.option import OptionDict, OptionBase, OptionSimplified


class AnswerNumberCount(TypedDict):
    value: int
    count: int


class QuestionAttributes(enum.Enum):
    indicator = "indicator"
    advance_filter = "advance_filter"
    generic_bar_chart = "generic_bar_chart"
    school_detail_popup = "school_detail_popup"


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
    jmp = "jmp"


class DependencyDict(TypedDict):
    id: int
    options: List[str]


class QuestionFormatted(TypedDict):
    id: int
    name: str
    option: Optional[List[OptionDict]] = []


class QuestionFormattedWithAttributes(TypedDict):
    id: Union[int, str]
    group: str
    name: str
    type: QuestionType
    attributes: Optional[List[QuestionAttributes]] = []
    option: Optional[List[OptionSimplified]] = []
    number: Optional[List[AnswerNumberCount]] = []


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
    attributes = Column(pg.ARRAY(String), nullable=True)
    display_name = Column(String, nullable=True)

    option = relationship(
        "Option",
        cascade="all, delete",
        passive_deletes=True,
        backref="option"
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
        attributes: Optional[List[QuestionAttributes]] = None,
        display_name: Optional[str] = None
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
        self.attributes = attributes
        self.display_name = display_name

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

    @property
    def formatted(self) -> QuestionFormatted:
        return {
            "id": self.id,
            "name": self.name,
            "option": [o.serialize for o in self.option] or [],
        }

    @property
    def formatted_with_attributes(self) -> QuestionFormattedWithAttributes:
        return {
            "id": self.id,
            "group": self.question.display_name or self.question.name,
            "name": self.display_name or self.name,
            "type": self.type.value,
            "attributes": self.attributes or [],
            "option": [o.simplify for o in self.option] or [],
            "number": []
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
    attributes: Optional[List[QuestionAttributes]]
    display_name: Optional[str]

    class Config:
        orm_mode = True


class QuestionIds(BaseModel):
    id: int
