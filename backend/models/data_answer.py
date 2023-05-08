from sqlalchemy import (
    Column, String, Integer, DateTime
)
import sqlalchemy.dialects.postgresql as pg
from db.connection import Base


class DataAnswer(Base):
    __tablename__ = "data_answer"
    id = Column(Integer, primary_key=True)
    identifier = Column(String)
    name = Column(String)
    geo = Column(String)
    created = Column(DateTime)
    answers = Column(pg.ARRAY(pg.JSONB))

    def __repr__(self) -> int:
        return f"<DataAnswer {self.id}>"

    @property
    def serialize(self):
        return {
            "id": self.id,
            "identifier": self.identifier,
            "name": self.name,
            "geo": self.geo,
            "created": self.created,
            "answers": self.answers
        }
