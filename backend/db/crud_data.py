from datetime import datetime
from typing import List, Optional
from typing_extensions import TypedDict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.data import Data, DataDict
from models.answer import Answer
from models.history import History
from models.answer import AnswerBase


class PaginatedData(TypedDict):
    data: List[DataDict]
    count: int


def add_data(
    session: Session, name: str, form: int, registration: bool,
    answers: List[AnswerBase], geo: Optional[List[float]] = None,
    id: Optional[int] = None, created: Optional[datetime] = None,
    updated: Optional[datetime] = None,
    identifier: Optional[str] = None,
    datapoint_id: Optional[int] = None,
) -> DataDict:
    data = Data(
        id=id, name=name, form=form, geo=geo,
        created=created if created else datetime.now(),
        updated=updated, identifier=identifier,
        datapoint_id=datapoint_id, registration=registration)
    for answer in answers:
        data.answer.append(answer)
    session.add(data)
    session.commit()
    session.flush()
    session.refresh(data)
    return data


def update_data(session: Session, data: Data) -> DataDict:
    session.commit()
    session.flush()
    session.refresh(data)
    return data


def delete_by_id(session: Session, id: int) -> None:
    session.query(History).filter(History.data == id).delete()
    session.query(Answer).filter(Answer.data == id).delete()
    session.query(Data).filter(Data.id == id).delete()
    session.commit()


def delete_bulk(session: Session, ids: List[int]) -> None:
    session.query(History).filter(
        History.data.in_(ids)).delete(synchronize_session='fetch')
    session.query(Answer).filter(
        Answer.data.in_(ids)).delete(synchronize_session='fetch')
    session.query(Data).filter(
        Data.id.in_(ids)).delete(synchronize_session='fetch')
    session.commit()


def get_data(
    session: Session, form: int, skip: int, perpage: int,
    options: List[str] = None, question: List[int] = None
) -> PaginatedData:
    data = session.query(Data).filter(Data.form == form)
    count = data.count()
    data = data.order_by(desc(Data.id))
    data = data.offset(skip).limit(perpage).all()
    return PaginatedData(data=data, count=count)


def get_data_by_id(session: Session, id: int) -> DataDict:
    return session.query(Data).filter(Data.id == id).first()


def get_data_by_datapoint_id(
    session: Session, datapoint_id: int, form: Optional[int] = None
) -> DataDict:
    data = session.query(Data).filter(Data.datapoint_id == datapoint_id)
    if form:
        data = data.filter(Data.form == form)
    return data.first()


def get_data_by_identifier(
    session: Session, identifier: str, form: Optional[int] = None
) -> DataDict:
    data = session.query(Data).filter(Data.identifier == identifier)
    if form:
        data = data.filter(Data.form == form)
    return data.first()
