from typing import List, Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session
from models.question import Question
from models.question import (
    QuestionDict,
    QuestionBase,
    QuestionType,
)
from models.option import Option, OptionDict
# import db.crud_option as crud_option


def get_last_question(session: Session, form: int, question_group: int):
    last_question = (
        session.query(Question)
        .filter(
            and_(
                Question.form == form,
                Question.question_group == question_group,
            )
        )
        .order_by(Question.order.desc())
        .first()
    )
    if last_question:
        last_question = last_question.order + 1
    else:
        last_question = 1
    return last_question


def generateOptionObj(obj: dict):
    opt = Option(name=obj["name"])
    if "id" in obj:
        opt.id = obj["id"]
    if "order" in obj:
        opt.order = obj["order"]
    if "code" in obj:
        opt.code = obj["code"]
    if "color" in obj:
        opt.color = obj["color"]
    if "description" in obj:
        opt.description = obj["description"]
    return opt


def add_question(
    session: Session,
    name: str,
    form: int,
    question_group: int,
    type: QuestionType,
    meta: bool,
    meta_geo: bool,
    id: Optional[int] = None,
    order: Optional[int] = None,
    option: Optional[List[OptionDict]] = None,
    required: Optional[bool] = True,
    dependency: Optional[List[dict]] = None,
    attributes: Optional[List[str]] = None,
    display_name: Optional[str] = None
) -> QuestionBase:
    last_question = get_last_question(
        session=session, form=form, question_group=question_group
    )
    question = Question(
        id=id,
        name=name,
        order=order if order else last_question,
        question_group=question_group,
        form=form,
        meta=meta,
        meta_geo=meta_geo if meta_geo else False,
        type=type,
        required=required,
        dependency=dependency,
        attributes=attributes,
        display_name=display_name
    )
    if option:
        for o in option:
            opt = generateOptionObj(obj=o)
            question.option.append(opt)
    session.add(question)
    session.commit()
    session.flush()
    session.refresh(question)
    return question


# def update_question(
#     session: Session,
#     name: str,
#     form: int,
#     question_group: int,
#     type: QuestionType,
#     meta: bool,
#     meta_geo: bool,
#     id: int,
#     order: Optional[int] = None,
#     option: Optional[List[OptionDict]] = None,
#     required: Optional[bool] = True,
#     dependency: Optional[List[dict]] = None,
# ) -> QuestionBase:
#     last_question = get_last_question(
#         session=session, form=form, question_group=question_group
#     )
#     question = (
#         session.query(Question)
#         .filter(and_(Question.form == form, Question.id == id))
#         .first()
#     )
#     # clear option when question type change
#     if question.type in [QuestionType.option, QuestionType.multiple_option]:
#         session.query(Option).filter(Option.question == question.id).delete(
#             synchronize_session="fetch"
#         )
#     question.name = name
#     question.order = order if order else last_question
#     question.meta = meta
#     question.meta_geo = meta_geo if meta_geo else False
#     question.question_group = question_group
#     question.type = type
#     question.required = required
#     question.dependency = dependency
#     if option:
#         for o in option:
#             find_option = (
#                 session.query(Option).filter(Option.id == o["id"]).first()
#             )
#             if not find_option:
#                 opt = opt = generateOptionObj(obj=o)
#                 question.option.append(opt)
#             if find_option:
#                 crud_option.update_option(
#                     session=session,
#                     id=o.get("id"),
#                     name=o.get("name"),
#                     order=o.get("order"),
#                     code=o.get("code"),
#                 )
#     session.commit()
#     session.flush()
#     session.refresh(question)
#     return question


def get_question(
    session: Session,
    form: Optional[int] = None,
    type: Optional[QuestionType] = None,
) -> List[QuestionDict]:
    if form:
        return session.query(Question).filter(Question.form == form).all()
    if form and type:
        return (
            session.query(Question)
            .filter(and_(Question.form == form, Question.type == type))
            .all()
        )
    return session.query(Question).all()


def get_question_by_id(session: Session, id: int) -> QuestionDict:
    return session.query(Question).filter(Question.id == id).first()


def get_question_by_ids(
    session: Session, ids: List[int]
) -> List[QuestionDict]:
    return session.query(Question).filter(Question.id.in_(ids)).all()


# def validate_dependency(session: Session, dependency: List[dict]):
#     # TODO: need to allow dependency for number and date
#     errors = []
#     for question in dependency:
#         qid = question["id"]
#         opt = question["options"]
#         if not len(opt):
#             errors.append("Should have at least 1 option")
#         question = get_question_by_id(session=session, id=qid)
#         if not question:
#             errors.append(f"Question {qid} not found")
#         if question.type not in [
#             QuestionType.option,
#             QuestionType.multiple_option,
#         ]:
#             errors.append(f"Question {qid} type should be option")
#         options = [o.name for o in question.option]
#         for o in opt:
#             if o not in options:
#                 errors.append(f"Option {o} is not part of {qid}")
#     return errors


# def delete_by_form(session: Session, form: int) -> None:
#     session.query(Question).filter(Question.form == form).delete()
#     session.commit()
