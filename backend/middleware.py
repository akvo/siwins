import re
from fastapi import HTTPException
from typing import Optional, List
from models.question import QuestionType
from db.crud_question import get_question_by_id
from db.crud_answer import get_answer_by_question
from sqlalchemy.orm import Session

query_pattern = re.compile(r"[0-9]*\|(.*)")


def check_jmp_query(keywords):
    jmp_query = []
    non_jmp_query = []
    if not keywords:
        return jmp_query, non_jmp_query
    for q in keywords:
        if "jmp" not in q:
            non_jmp_query.append(q)
            continue
        jmp_query.append(q.split("-")[1].lower())
    return jmp_query, non_jmp_query


def check_query(keywords):
    keys = []
    if not keywords:
        return keys
    for q in keywords:
        if not query_pattern.match(q):
            raise HTTPException(
                status_code=400,
                detail="Bad Request, wrong q pattern")
        else:
            keys.append(q.replace("|", "||").lower())
    return keys


def check_indicator_query(
    session: Session,
    indicator: int,
    number: Optional[List[int]],
    return_answer_temp: Optional[bool] = True
):
    # 1. indicator filter by option,
    #  - use same format as advanced filter: q param = qid|option
    # 2. indicator filter by number,
    #  - check if indicator qtype is number
    #  - filter answers by number param
    question = get_question_by_id(session=session, id=indicator)
    is_number = question.type == QuestionType.number \
        if question else False
    if number and not is_number:
        raise HTTPException(
            status_code=400,
            detail="Bad Request, indicator is not number type")
    if number and len(number) != 2:
        raise HTTPException(
            status_code=400,
            detail="Bad Request, number param length must equal to 2")
    # get all answers by indicator
    answer_data_ids = None
    answer_temp = {}
    if indicator:
        answers = get_answer_by_question(
            session=session, question=indicator, number=number)
        answer_data_ids = [a.data for a in answers]
    if indicator and return_answer_temp:
        answers = [
            a.formatted_with_data for a in answers
        ] if answers else []
        for a in answers:
            key = a.get('identifier')
            del a['data']
            del a['identifier']
            answer_temp.update({key: a})
    return answer_data_ids, answer_temp
