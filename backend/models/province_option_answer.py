from sqlalchemy import (
    Column, BigInteger, String,
    Boolean, Integer
)
import sqlalchemy.dialects.postgresql as pg
from db.connection import Base


class ProvinceOptionAnswer(Base):
    __tablename__ = "province_option_answer"
    question = Column(BigInteger)
    type = Column(String)
    form = Column(BigInteger)
    current = Column(Boolean)
    year_conducted = Column(Integer)
    data_ids = Column(pg.ARRAY(Integer))
    province = Column(String)
    value = Column(String)
    count = Column(Integer)

    def __repr__(self) -> int:
        return f"<ProvinceOptionAnswer {self.question}>"

    @property
    def serialize(self):
        return {
            "question": self.question,
            "type": self.type,
            "form": self.form,
            "current": self.current,
            "year_conducted": self.year_conducted,
            "data_ids": self.data_ids,
            "province": self.province,
            "value": self.value,
            "count": self.count
        }
