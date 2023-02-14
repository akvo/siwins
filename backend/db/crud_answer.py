import json
from typing import List, Union, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from models.answer import Answer, AnswerDict, AnswerBase
from models.history import History, HistoryBase, HistoryDict
from models.question import QuestionType


def append_value(
    answer: Answer,
    value: Union[int, float, str, bool, List[str], List[int], List[float]],
    type: QuestionType,
) -> Answer:
    if type == QuestionType.number:
        answer.value = value
    if type == QuestionType.text:
        answer.text = value
    if type == QuestionType.date:
        answer.text = value
    if type == QuestionType.geo:
        answer.text = ("{}|{}").format(value.get("lat"), value.get("long"))
    if type == QuestionType.option:
        options = [
            v.get("name") if "name" in v else v.get("text") for v in value
        ]
        answer.options = options
    if type == QuestionType.multiple_option:
        options = [
            v.get("name") if "name" in v else v.get("text") for v in value
        ]
        answer.options = options
    if type == QuestionType.photo:
        answer.text = json.dumps(value)
    if type == QuestionType.geoshape:
        answer.text = json.dumps(value)
    return answer


def add_answer(
    session: Session,
    answer: Answer,
    type: QuestionType,
    value: Union[int, float, str, bool, List[str], List[int], List[float]],
) -> AnswerDict:
    answer = append_value(answer, value, type)
    session.add(answer)
    session.commit()
    session.flush()
    # session.refresh(answer)
    return answer


def add_history(session: Session, history: History) -> HistoryDict:
    session.add(history)
    session.commit()
    session.flush()
    # session.refresh(answer)
    return history


def update_answer(
    session: Session,
    answer: Answer,
    type: QuestionType,
    value: Union[int, float, str, bool, List[str], List[int], List[float]],
    history: Optional[History] = None,
) -> AnswerDict:
    # delete old answer
    delete_answer_by_id(session=session, id=answer.id)
    # add update answer
    new_answer = append_value(answer, value, type)
    if new_answer:
        session.add(new_answer)
    if history:
        session.add(history)
    session.commit()
    session.flush()
    # session.refresh(new_answer)
    return answer


def update_history(
    session: Session,
    history: History,
    type: QuestionType,
    value: Union[int, float, str, bool, List[str], List[int], List[float]],
) -> HistoryDict:
    # delete old history
    delete_history_by_id(session=session, id=history.id)
    # add update history
    new_history = append_value(history, value, type)
    if new_history:
        session.add(new_history)
    session.commit()
    session.flush()
    session.refresh(new_history)
    return history


def get_answer_by_question(
    session: Session, question: int
) -> List[AnswerDict]:
    return session.query(Answer).filter(Answer.question == question).all()


def get_answer_by_data_and_question(
    session: Session, data: int, questions: List[int]
) -> List[AnswerBase]:
    return (
        session.query(Answer)
        .filter(and_(Answer.question.in_(questions), Answer.data == data))
        .all()
    )


def get_history_by_data_and_question(
    session: Session, data: int, questions: List[int]
) -> List[HistoryBase]:
    return (
        session.query(History)
        .filter(and_(History.question.in_(questions), History.data == data))
        .all()
    )


def get_history(session: Session, data: int, question: int):
    answer = (
        session.query(Answer)
        .filter(and_(Answer.data == data, Answer.question == question))
        .first()
    )
    answer = answer.simplified
    history = (
        session.query(History)
        .filter(and_(History.data == data, History.question == question))
        .order_by(desc(History.id))
        .all()
    )
    history = [h.simplified for h in history]
    return [answer] + history


def delete_answer_by_id(session: Session, id: int) -> None:
    return session.query(Answer).filter(Answer.id == id).delete()


def get_answer_by_data(session: Session, data: int) -> List[AnswerBase]:
    return session.query(Answer).filter(Answer.data == data).all()


def delete_history_by_id(session: Session, id: int) -> None:
    return session.query(History).filter(History.id == id).delete()


def update_answer_from_history(
    session: Session, data: int, history: HistoryDict
) -> None:
    session.query(Answer).filter(
        and_(Answer.data == data, Answer.question == history["question"])
    ).update(
        {
            "text": history["text"],
            "value": history["value"],
            "options": history["options"],
            "created": history["created"],
            "updated": history["updated"],
        },
        synchronize_session="evaluate",
    )
    session.query(History).filter(History.data == history["data"]).delete()
