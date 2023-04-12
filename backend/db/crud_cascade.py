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


def get_cascade_by_question_id(session: Session, question: int) -> CascadeDict:
    return session.query(Cascade).filter(
        Cascade.question == question).order_by(Cascade.level).all()


def get_cascade_by_parent(session: Session, parent: int) -> CascadeSimplified:
    return session.query(Cascade).filter(
        Cascade.parent == parent).order_by(Cascade.level).all()
