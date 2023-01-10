from typing_extensions import TypedDict
from sqlalchemy import Column, Integer, Text
from typing import Optional
from db.connection import Base
from pydantic import BaseModel


class ViewDataScoreDict(TypedDict):
    data: int
    form: int
    question: Optional[int] = None
    option: Optional[str] = None
    score: Optional[int] = None


class GroupByDict(TypedDict):
    data: int
    option: str
    count: int
    score: int


class ViewDataScore(Base):
    __tablename__ = "score_view"
    data = Column(Integer, primary_key=True)
    form = Column(Integer)
    question = Column(Integer, nullable=True, primary_key=True)
    option = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)

    def __repr__(self) -> int:
        return f"<ViewDataScore {self.data} {self.question}>"

    @property
    def serialize(self) -> ViewDataScoreDict:
        return {
            "data": self.data,
            "form": self.form,
            "question": self.question,
            "option": self.option,
            "score": self.score,
        }

    @property
    def serialize_jmp_group_by_parent(self):
        return {
            "data": self.data,
            "option": self.option,
            "score": self.score,
        }

    @property
    def serialize_jmp_group_no_parent(self):
        return {
            "data": self.data,
            "option": self.option,
            "score": self.score,
        }

    def group_serialize(data) -> GroupByDict:
        return {
            "data": data.data,
            "option": data.option,
            "count": data.count,
        }


class ViewDataScoreBase(BaseModel):
    data: int
    form: int
    question: Optional[int] = None
    option: Optional[str] = None
    score: Optional[int] = None

    class Config:
        orm_mode = True
