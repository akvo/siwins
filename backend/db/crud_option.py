from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.option import Option, OptionDict
from models.question import Question


def get_option(session: Session) -> List[OptionDict]:
    return session.query(Option).all()


def get_option_by_question_id(
    session: Session,
    question=int,
) -> List[OptionDict]:
    return session.query(Option).filter(Option.question == question).all()


def add_option(
    session: Session,
    question=int,
    name=str,
    id=Optional[int],
    order=Optional[str],
    code: Optional[str] = None,
) -> OptionDict:
    question = session.query(Question).filter(Question.id == question).first()
    option = Option(name=name, order=order, code=code)
    question.option.append(option)
    session.flush()
    session.commit()
    session.refresh(option)
    return option


def update_option(
    session: Session,
    id: int,
    name: Optional[str] = None,
    order: Optional[str] = None,
    code: Optional[str] = None,
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


def update_score(
    session: Session, question: int, names: List[str], score: int
):
    print(f"score: {score}")
    session.query(Option).filter(
        and_(Option.question == question, Option.name.in_(names))
    ).update({Option.score: score}, synchronize_session=False)
    session.flush()
    session.commit()
