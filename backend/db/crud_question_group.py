from typing import Optional
from sqlalchemy.orm import Session
from models.question_group import QuestionGroup, QuestionGroupDict
# from sqlalchemy import and_


def get_last_question_group(session: Session, form: int):
    last_question_group = (
        session.query(QuestionGroup)
        .filter(QuestionGroup.form == form)
        .order_by(QuestionGroup.order.desc())
        .first()
    )
    if last_question_group:
        last_question_group = last_question_group.order + 1
    else:
        last_question_group = 1
    return last_question_group


def add_question_group(
    session: Session,
    form: int,
    name: str,
    id: Optional[int] = None,
    order: Optional[int] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    repeatable: Optional[bool] = False,
) -> QuestionGroupDict:
    last_question_group = get_last_question_group(session=session, form=form)
    question_group = QuestionGroup(
        id=id,
        name=name,
        form=form,
        order=order if order else last_question_group,
        display_name=display_name,
        description=description,
        repeatable=repeatable,
    )
    session.add(question_group)
    session.commit()
    session.flush()
    session.refresh(question_group)
    return question_group


# def update_question_group(
#     session: Session,
#     form: int,
#     name: str,
#     id: int,
#     order: Optional[int] = None,
#     description: Optional[str] = None,
#     repeatable: Optional[bool] = False,
# ) -> QuestionGroupDict:
#     last_question_group = get_last_question_group(session=session, form=form)
#     question_group = (
#         session.query(QuestionGroup)
#         .filter(and_(QuestionGroup.form == form, QuestionGroup.id == id))
#         .first()
#     )
#     question_group.name = (name,)
#     question_group.order = order if order else last_question_group
#     question_group.description = description
#     question_group.repeatable = repeatable
#     session.commit()
#     session.flush()
#     session.refresh(question_group)
#     return question_group


# def delete_by_form(session: Session, form: int) -> None:
#     session.query(QuestionGroup).filter(QuestionGroup.form == form).delete()
#     session.commit()
