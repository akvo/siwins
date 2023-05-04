# Please don't use **kwargs
# Keep the code clean and CLEAR

from typing import Optional, List
from typing_extensions import TypedDict
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import Text, Boolean, BigInteger
from sqlalchemy.orm import relationship
from db.connection import Base
from models.question import QuestionBase


class QuestionGroupDict(TypedDict):
    id: int
    form: int
    name: str
    order: Optional[int] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    repeatable: Optional[bool] = False


class QuestionGroup(Base):
    __tablename__ = "question_group"
    id = Column(BigInteger, primary_key=True, index=True, nullable=True)
    form = Column(BigInteger, ForeignKey("form.id"))
    name = Column(String)
    display_name = Column(String, nullable=True)
    order = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    repeatable = Column(Boolean, nullable=True)

    question = relationship(
        "Question",
        cascade="all, delete",
        passive_deletes=True,
        backref="question",
    )

    def __init__(
        self,
        id: Optional[int],
        name: str,
        form: form,
        order: order,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        repeatable: Optional[bool] = False,
    ):
        self.id = id
        self.name = name
        self.form = form
        self.order = order
        self.display_name = display_name
        self.description = description
        self.repeatable = repeatable

    def __repr__(self) -> int:
        return f"<QuestionGroup {self.id}>"

    @property
    def serialize(self) -> QuestionGroupDict:
        return {
            "id": self.id,
            "form": self.form,
            "question": self.question,
            "name": self.name,
            "order": self.order,
            "display_name": self.display_name,
            "description": self.description,
            "repeatable": self.repeatable,
        }


class QuestionGroupBase(BaseModel):
    id: int
    form: int
    name: str
    order: Optional[int] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    repeatable: Optional[bool] = False
    question: List[QuestionBase]

    class Config:
        orm_mode = True
