# Please don't use **kwargs
# Keep the code clean and CLEAR

from typing_extensions import TypedDict
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Column, BigInteger, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from db.connection import Base
from models.question_group import QuestionGroupBase


class FormDict(TypedDict):
    id: int
    name: str
    version: Optional[float]
    description: Optional[str]
    registration_form: Optional[int]


class Form(Base):
    __tablename__ = "form"
    id = Column(BigInteger, primary_key=True, index=True, nullable=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    version = Column(Float, nullable=True, default=0.0)
    registration_form = Column(BigInteger, ForeignKey('form.id'))

    question_group = relationship(
        "QuestionGroup", cascade="all, delete",
        passive_deletes=True, backref="question_group")

    def __init__(
        self,
        id: Optional[int],
        name: str,
        version: Optional[float] = 0.0,
        description: Optional[str] = None,
        registration_form: Optional[int] = None
    ):
        self.id = id
        self.name = name
        self.version = version
        self.description = description
        self.registration_form = registration_form

    def __repr__(self) -> int:
        return f"<Form {self.id}>"

    @property
    def serialize(self) -> FormDict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "registration_form": self.registration_form
        }


class FormBase(BaseModel):
    id: int
    name: str
    version: Optional[float]
    description: Optional[str]
    registration_form: Optional[int]
    question_group: List[QuestionGroupBase]

    class Config:
        orm_mode = True
