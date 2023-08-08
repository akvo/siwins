# Please don't use **kwargs
# Keep the code clean and CLEAR

from urllib.parse import urlparse, parse_qs
from typing_extensions import TypedDict
from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy import Integer, Text
from db.connection import Base


class SyncDict(TypedDict):
    id: int
    url: str


class Sync(Base):
    __tablename__ = "sync"
    id = Column(Integer, primary_key=True, index=True, nullable=True)
    url = Column(Text)

    def __init__(self, url: str):
        self.url = url

    def __repr__(self) -> int:
        return f"<Sync {self.id}>"

    @property
    def serialize(self) -> SyncDict:
        return {
            "id": self.id,
            "url": self.url,
        }

    @property
    def get_cursor(self):
        url = self.url
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        cursor_value = query_params.get("cursor", [None])[0]
        return cursor_value


class SyncBase(BaseModel):
    id: int
    url: str

    class Config:
        orm_mode = True
