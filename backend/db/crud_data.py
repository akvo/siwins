from datetime import datetime
from typing import List, Optional
from typing_extensions import TypedDict
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, select, or_
from sqlalchemy.sql.expression import false
from models.data import Data, DataDict
from models.answer import Answer
from models.history import History
from models.answer import AnswerBase
from models.history import HistoryDict
from models.advance_filter import ViewAdvanceFilter
from sqlalchemy.orm import aliased


class PaginatedData(TypedDict):
    data: List[DataDict]
    count: int


def add_data(
    session: Session,
    name: str,
    form: int,
    registration: bool,
    answers: List[AnswerBase],
    geo: Optional[List[float]] = None,
    id: Optional[int] = None,
    created: Optional[datetime] = None,
    updated: Optional[datetime] = None,
    identifier: Optional[str] = None,
    datapoint_id: Optional[int] = None,
) -> DataDict:
    data = Data(
        id=id,
        name=name,
        form=form,
        geo=geo,
        created=created if created else datetime.now(),
        updated=updated,
        identifier=identifier,
        datapoint_id=datapoint_id,
        registration=registration,
    )
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
    session.query(History).filter(History.data.in_(ids)).delete(
        synchronize_session="fetch"
    )
    session.query(Answer).filter(Answer.data.in_(ids)).delete(
        synchronize_session="fetch"
    )
    session.query(Data).filter(Data.id.in_(ids)).delete(
        synchronize_session="fetch"
    )
    session.commit()


def get_data(
    session: Session,
    form: int,
    skip: int,
    perpage: int,
    options: List[str] = None,
    question: List[int] = None,
) -> PaginatedData:
    data = session.query(Data).filter(Data.form == form)
    count = data.count()
    data = data.order_by(desc(Data.id))
    data = data.offset(skip).limit(perpage).all()
    return PaginatedData(data=data, count=count)


def get_all_data(
    session: Session,
    registration: bool,
    options: List[str] = None,
) -> DataDict:
    data = session.query(Data).filter(Data.registration == registration).all()
    if options:
        # support multiple select options filter
        # change query to filter data by or_ condition
        or_query = or_(
            ViewAdvanceFilter.options.contains([opt]) for opt in options
        )
        data_id = session.query(ViewAdvanceFilter.data).filter(or_query).all()
        data = data.filter(Data.id.in_([d.data for d in data_id]))
    return data


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
    return data.order_by(desc(Data.created)).first()


def get_monitoring_data(session: Session, identifier: str):
    return (
        session.query(Data)
        .filter(
            and_(Data.identifier == identifier, Data.registration == false())
        )
        .all()
    )


def get_registration_only(session: Session):
    nodealias = aliased(Data)
    adp = session.scalars(
        select(Data).join(Data.monitoring.of_type(nodealias))
    ).all()
    ids = [d.datapoint_id if d else None for d in adp]
    return (
        session.query(Data)
        .filter(and_(Data.datapoint_id.is_(None), Data.id.not_in(ids)))
        .first()
    )


def get_monitoring_by_id(session: Session, datapoint: Data) -> DataDict:
    nodealias = aliased(Data)
    return session.scalars(
        select(Data)
        .where(Data.datapoint_id == datapoint.id)
        .join(Data.monitoring.of_type(nodealias))
    ).first()


def get_last_history(
    session: Session, datapoint_id: int, id: int
) -> List[HistoryDict]:
    data = (
        session.query(Data)
        .filter(and_(Data.datapoint_id == datapoint_id, Data.id != id))
        .order_by(desc(Data.created))
        .first()
    )
    return [h.serialize for h in data.history] if data else []
