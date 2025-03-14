from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.option import Option, OptionDict
from models.data import Data

# from models.question import Question

from source.main import main_config

QuestionConfig = main_config.QuestionConfig


year_conducted_qid = QuestionConfig.year_conducted.value

# def get_option(session: Session) -> List[OptionDict]:
#     return session.query(Option).all()


def get_option_by_question_id(
    session: Session, question=int, columns: Optional[List] = None
) -> List[OptionDict]:
    columns = columns if columns else [Option]
    return session.query(*columns).filter(Option.question == question).all()


def get_option_year_conducted(session: Session) -> List[OptionDict]:
    # filter by available year conducted in data table
    data_year_conducted = session.query(Data.year_conducted).distinct().all()
    data_year_conducted = [str(d[0]) for d in data_year_conducted]
    return (
        session.query(Option)
        .filter(
            and_(
                Option.question == year_conducted_qid,
                Option.name.in_(data_year_conducted),
            )
        )
        .all()
    )


# def add_option(
#     session: Session,
#     question=int,
#     name=str,
#     id=Optional[int],
#     order=Optional[str],
#     code: Optional[str] = None,
# ) -> OptionDict:
#     question = session.query(Question).filter(
#       Question.id == question).first()
#     option = Option(name=name, order=order, code=code)
#     question.option.append(option)
#     session.flush()
#     session.commit()
#     session.refresh(option)
#     return option


# def update_option(
#     session: Session,
#     id: int,
#     name: Optional[str] = None,
#     order: Optional[str] = None,
#     code: Optional[str] = None,
# ) -> OptionDict:
#     option = session.query(Option).filter(Option.id == id).first()
#     option.order = order
#     option.code = code
#     if name:
#         option.name = name
#     session.flush()
#     session.commit()
#     session.refresh(option)
#     return option
