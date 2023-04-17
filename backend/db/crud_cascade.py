from typing import Optional
from sqlalchemy.orm import Session
from models.cascade import Cascade, CascadeDict, CascadeSimplified


def add_cascade(session: Session, data: Cascade) -> CascadeDict:
    session.add(data)
    session.commit()
    session.flush()
    session.refresh(data)
    return data


def get_all_cascade(session: Session) -> CascadeDict:
    return session.query(Cascade).order_by(Cascade.level).all()


def get_cascade_by_question_id(
    session: Session,
    question: int,
    level: Optional[int] = None,
    distinct: Optional[bool] = False
) -> CascadeDict:
    cascade = session.query(Cascade).filter(
        Cascade.question == question)
    if level is not None:
        cascade = cascade.filter(Cascade.level == level)
    if distinct:
        cascade = cascade.distinct(Cascade.name, Cascade.level)
    return cascade.order_by(Cascade.level).all()


def get_cascade_by_parent(
    session: Session, parent: int, level: Optional[int] = None
) -> CascadeSimplified:
    cascade = session.query(Cascade).filter(
        Cascade.parent == parent)
    if level is not None:
        cascade = cascade.filter(Cascade.level == level)
    return cascade.order_by(Cascade.level).all()
