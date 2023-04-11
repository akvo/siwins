# Please don't use **kwargs
# Keep the code clean and CLEAR

from typing_extensions import TypedDict
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.connection import Base


class CascadeDict(TypedDict):
    id: int
    parent: Optional[int] = None
    name: str
    level: int
    children: Optional[List] = []


class Cascade(Base):
    __tablename__ = "cascade"
    id = Column(Integer, primary_key=True, index=True, nullable=True)
    parent = Column(Integer, ForeignKey('cascade.id'), nullable=True)
    name = Column(String)
    level = Column(Integer)
    children = relationship("cascade")
    parent_detail = relationship(
        "cascade", remote_side=[id], overlaps="children")

    def __init__(
        self, id: int, parent: int,
        name: str, level: int
    ):
        self.id = id
        self.parent = parent
        self.name = name
        self.level = level

    def __repr__(self) -> int:
        return f"<Cascade {self.id}>"

    @property
    def serialize(self) -> CascadeDict:
        return {
            "id": self.id,
            "parent": self.parent,
            "name": self.name,
            "level": self.level,
            "children": self.children
        }


class CascadeBase(BaseModel):
    id: int
    parent: Optional[int] = None
    name: str
    level: int

    class Config:
        orm_mode = True
