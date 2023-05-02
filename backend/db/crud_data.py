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
    current: Optional[bool] = False,
    geo: Optional[List[float]] = None,
    id: Optional[int] = None,
    created: Optional[datetime] = None,
    updated: Optional[datetime] = None,
    identifier: Optional[str] = None,
    datapoint_id: Optional[int] = None,
    year_conducted: Optional[int] = None,
    school_information: Optional[List[str]] = None,
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
        year_conducted=year_conducted,
        school_information=school_information,
        current=current
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


# for paginated data purpose
def get_data(
    session: Session,
    skip: int,
    perpage: int,
    form: Optional[int] = None,
    registration: Optional[bool] = None,
    options: List[str] = None,
    question: List[int] = None,
) -> PaginatedData:
    data = session.query(Data)
    if form:
        data = data.filter(Data.form == form)
    if registration is not None:
        data = data.filter(Data.registration == registration)
    count = data.count()
    data = data.order_by(desc(Data.id))
    data = data.offset(skip).limit(perpage).all()
    return PaginatedData(data=data, count=count)


# get all data with filtered value
def get_all_data(
    session: Session,
    registration: Optional[bool] = None,
    current: Optional[bool] = None,
    options: Optional[List[str]] = None,
    data_ids: Optional[List[int]] = None,
    prov: Optional[List[str]] = None,
    sctype: Optional[List[str]] = None,
    count: Optional[bool] = False
) -> DataDict:
    data = session.query(Data)
    if registration is not None:
        data = data.filter(
            Data.registration == registration)
    if current is not None:
        data = data.filter(Data.current == current)
    if options:
        # support multiple select options filter
        # change query to filter data by or_ condition
        or_query = or_(
            ViewAdvanceFilter.options.contains([opt]) for opt in options
        )
        data_id = session.query(
            ViewAdvanceFilter.identifier).filter(or_query).all()
        data = data.filter(Data.identifier.in_(
            [d.identifier for d in data_id]))
    if data_ids is not None:
        data = data.filter(Data.id.in_(data_ids))
    if prov:
        or_query = or_(
            Data.school_information.contains([v]) for v in prov)
        data = data.filter(or_query)
    if sctype:
        or_query = or_(
            Data.school_information.contains([v]) for v in sctype)
        data = data.filter(or_query)
    if count:
        return data.count()
    data = data.all()
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


# only for fake datapoint seeder
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


# not used
# def get_monitoring_by_id(session: Session, datapoint: Data) -> DataDict:
#     nodealias = aliased(Data)
#     return session.scalars(
#         select(Data)
#         .where(Data.datapoint_id == datapoint.id)
#         .join(Data.monitoring.of_type(nodealias))
#     ).first()


# used on data_sync
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


def get_data_by_year_conducted(session: Session, year_conducted: int):
    return session.query(Data).filter(
        Data.year_conducted == year_conducted).all()


def get_data_by_school(
    session: Session,
    schools: List[str],
    year_conducted: Optional[int] = None
):
    data = session.query(Data)
    and_query = and_(
        Data.school_information.contains([v]) for v in schools)
    data = data.filter(and_query)
    if (year_conducted):
        data = data.filter(Data.year_conducted == year_conducted)
    return data.first()


def get_history_data_by_school(
    session: Session,
    schools: List[str],
    year_conducted: Optional[int] = None
):
    data = session.query(Data)
    and_query = and_(
        Data.school_information.contains([v]) for v in schools)
    data = data.filter(and_query).filter(Data.current == false())
    if (year_conducted):
        data = data.filter(Data.year_conducted < year_conducted)
    return data.all()


def get_year_conducted_from_datapoint(session: Session):
    return session.query(Data.year_conducted, Data.current).distinct(
        Data.year_conducted).order_by(
            desc(Data.year_conducted)).all()
