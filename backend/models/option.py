# Please don't use **kwargs
# Keep the code clean and CLEAR

from typing import Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy import Integer, String, BigInteger
from db.connection import Base


class OptionDict(TypedDict):
    id: int
    name: str
    order: Optional[int] = None
    code: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class OptionSimplified(TypedDict):
    name: str
    order: Optional[int] = None
    color: Optional[str] = None
    description: Optional[str] = None


class Option(Base):
    __tablename__ = "option"
    id = Column(Integer, primary_key=True, index=True, nullable=True)
    question = Column(BigInteger, ForeignKey("question.id"))
    name = Column(String)
    order = Column(Integer, nullable=True)
    code = Column(String, nullable=True)
    color = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    def __init__(
        self,
        name: str,
        id: Optional[int] = None,
        order: Optional[int] = None,
        code: Optional[str] = None,
        color: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.order = order
        self.code = code
        self.color = color
        self.description = description

    def __repr__(self) -> int:
        return f"<Option {self.id}>"

    @property
    def serialize(self) -> OptionDict:
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "code": self.code,
            "color": self.color,
            "description": self.description,
        }

    @property
    def simplify(self) -> OptionSimplified:
        return {
            "name": self.name,
            "order": self.order,
            "color": self.color,
            "description": self.description,
        }


class OptionBase(BaseModel):
    id: int
    name: str
    order: Optional[int] = None
    code: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
