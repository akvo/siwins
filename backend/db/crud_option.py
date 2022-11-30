from typing import List, Optional
from sqlalchemy.orm import Session
from models.option import Option, OptionDict
from models.question import Question


def get_option(session: Session) -> List[OptionDict]:
    return session.query(Option).all()


def add_option(
    session: Session, question=int, name=str,
    id=Optional[int], order=Optional[str], code: Optional[str] = None
) -> OptionDict:
    question = session.query(Question).filter(Question.id == question).first()
    option = Option(name=name, order=order, code=code)
    question.option.append(option)
    session.flush()
    session.commit()
    session.refresh(option)
    return option


def update_option(
    session: Session, id: int, name: Optional[str] = None,
    order: Optional[str] = None, code: Optional[str] = None,
) -> OptionDict:
    option = session.query(Option).filter(Option.id == id).first()
    option.order = order
    option.code = code
    if name:
        option.name = name
    session.flush()
    session.commit()
    session.refresh(option)
    return option
