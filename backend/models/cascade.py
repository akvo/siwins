# Please don't use **kwargs
# Keep the code clean and CLEAR

from typing_extensions import TypedDict
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, \
    ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from db.connection import Base
from models.question import Question


class CascadeDict(TypedDict):
    id: int
    parent: Optional[int] = None
    name: str
    level: int
    question: int
    children: Optional[List] = []


class CascadeSimplified(TypedDict):
    id: int
    parent: Optional[int] = None
    name: str


class CascadeNameAndLevel(TypedDict):
    name: str
    level: int


class Cascade(Base):
    __tablename__ = "cascade"
    id = Column(Integer, primary_key=True, index=True, nullable=True)
    parent = Column(Integer, ForeignKey('cascade.id'), nullable=True)
    name = Column(String)
    level = Column(Integer)
    question = Column(BigInteger, ForeignKey('question.id'))
    question_detail = relationship(Question, foreign_keys=[question])
    children = relationship("Cascade")
    parent_detail = relationship(
        "Cascade", remote_side=[id], overlaps="children")

    def __init__(
        self, id: int, parent: int,
        name: str, level: int, question: int
    ):
        self.id = id
        self.parent = parent
        self.name = name
        self.level = level
        self.question = question

    def __repr__(self) -> int:
        return f"<Cascade {self.id}>"

    @property
    def serialize(self) -> CascadeDict:
        return {
            "id": self.id,
            "parent": self.parent,
            "name": self.name,
            "level": self.level,
            "question": self.question,
            "children": self.children
        }

    @property
    def simplify(self) -> CascadeSimplified:
        return {
            "id": self.id,
            "parent": self.parent,
            "name": self.name,
        }

    @property
    def to_name_level(self) -> CascadeNameAndLevel:
        return {
            "name": self.name,
            "level": self.level,
        }


class CascadeBase(BaseModel):
    id: int
    parent: Optional[int] = None
    name: str
    level: int
    question: int

    class Config:
        orm_mode = True
