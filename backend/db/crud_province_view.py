from typing import List
from sqlalchemy.orm import Session
from models.province_number_answer import ProvinceNumberAnswer


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
