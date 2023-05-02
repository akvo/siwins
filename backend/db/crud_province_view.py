from typing import List
from sqlalchemy.orm import Session
from models.province_number_answer import (
    ProvinceNumberAnswer
)
from models.province_option_answer import (
    ProvinceOptionAnswer
)


def get_province_number_answer(
    session: Session,
    question_ids: List[int],
    current: bool
):
    return session.query(
        ProvinceNumberAnswer
    ).filter(
        ProvinceNumberAnswer.question.in_(question_ids)
    ).filter(
        ProvinceNumberAnswer.current == current
    ).all()


def get_province_option_answer(
    session: Session,
    question_ids: List[int],
    current: bool
):
    return session.query(
        ProvinceOptionAnswer
    ).filter(
        ProvinceOptionAnswer.question.in_(question_ids)
    ).filter(
        ProvinceOptionAnswer.current == current
    ).all()
