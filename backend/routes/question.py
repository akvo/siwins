import os
from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from typing import List, Optional
from sqlalchemy.orm import Session
from db.crud_question import (
    get_question, get_question_by_attributes
)
from db.crud_jmp import (
    get_jmp_config
)
from db.connection import get_session
from models.question import QuestionFormattedWithAttributes
from models.question import QuestionAttributes, QuestionType
from models.answer import Answer
from models.history import History

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

security = HTTPBearer()
question_route = APIRouter()


@question_route.get(
    "/question",
    response_model=List[QuestionFormattedWithAttributes],
    summary="get all questions",
    name="question:get_all_question",
    tags=["Question"],
)
def get(
    req: Request,
    attribute: Optional[QuestionAttributes] = None,
    session: Session = Depends(get_session)
):
    questions = []
    # collect all question / with attributes
    if not attribute:
        question = get_question(session=session)
        question = [q.formatted_with_attributes for q in question]
    if attribute == QuestionAttributes.indicator:
        jmp_configs = get_jmp_config()
        for jc in jmp_configs:
            name = jc.get("name")
            labels = jc.get("labels")
            for lbi, lb in enumerate(labels):
                lb["order"] = lbi + 1
                lb["description"] = None
            questions.append({
                "id": f"jmp-{name.lower() if name else lbi}",
                "group": "JMP Indicator",
                "name": name,
                "type": "jmp",
                "attributes": ["indicator"],
                "option": labels,
                "number": []
            })
    if attribute:
        question = get_question_by_attributes(
            session=session, attribute=attribute.value)
        # get answer number values
        number_qids = []
        for q in question:
            if q.type != QuestionType.number:
                continue
            number_qids.append(q.id)
        answers = session.query(Answer).filter(
            Answer.question.in_(number_qids)).all()
        histories = session.query(History).filter(
            History.question.in_(number_qids)).all()
        answer_values = {}
        for a in answers + histories:
            key = a.question
            if key not in answer_values:
                answer_values.update({key: [a.value]})
            else:
                answer_values.update({key: answer_values[key] + [a.value]})
        # EOL number values
        question = [q.formatted_with_attributes for q in question]
        for q in question:
            key = q.get('id')
            # nadd umber value to question
            numbers = []
            numb_val = answer_values.get(int(key)) or []
            count_numb = {x: numb_val.count(x) for x in numb_val}
            for val, count in count_numb.items():
                numbers.append({"value": val, "count": count})
            numbers.sort(key=lambda x: x.get('value'))
            q['number'] = numbers
    return questions + question
