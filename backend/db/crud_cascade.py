from typing import Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session
from models.cascade import Cascade, CascadeDict, CascadeSimplified

from source.main import main_config

QuestionConfig = main_config.QuestionConfig
SchoolInformationEnum = main_config.SchoolInformationEnum
CascadeLevels = main_config.CascadeLevels


school_information_qid = QuestionConfig.school_information.value
province_enum = SchoolInformationEnum.province.value
province_level = CascadeLevels.school_information.value[province_enum]


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


def get_province_of_school_information(session: Session):
    return session.query(Cascade).filter(and_(
        Cascade.question == school_information_qid,
        Cascade.level == province_level
    )).all()
