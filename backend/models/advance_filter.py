from sqlalchemy import Column, Integer, Text
import sqlalchemy.dialects.postgresql as pg
from db.connection import Base


class ViewAdvanceFilter(Base):
    __tablename__ = "advance_filter"
    data = Column(Integer, primary_key=True)
    options = Column(pg.ARRAY(Text))
    identifier = Column(Text, nullable=True)

    def __repr__(self) -> int:
        return f"<ViewAdvanceFilter {self.data}>"

    @property
    def raw(self):
        opt = self.options
        opt_data = []
        for o in opt:
            d = o.split("||")
            opt_data.append(
                {"id": self.data, "question": d[0], "answer": d[1]}
            )
        return opt_data
