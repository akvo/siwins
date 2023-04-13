import os
import json
from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from typing import List, Optional
from sqlalchemy.orm import Session
from db import crud_question, crud_form
from db.connection import get_session
from models.question import QuestionFormattedWithAttributes
from models.question import QuestionAttributes, QuestionType
from models.answer import Answer
from models.history import History
from source.main_config import FORM_PATH

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
    # collect all question attributes
    question_attributes = {}
    if not attribute:
        question = crud_question.get_question(session=session)
    if attribute:
        qids = []
        # TODO: add attributes column into question table ?
        forms = crud_form.get_form(session=session)
        for f in forms:
            form_file = f"{FORM_PATH}/{f.id}.json"
            json_form = {}
            with open(form_file) as json_file:
                json_form = json.load(json_file)
            question_groups = json_form.get("questionGroup")
            if isinstance(question_groups, dict):
                question_groups = [question_groups]
            for qg in question_groups:
                questions = qg.get('question')
                if isinstance(questions, dict):
                    questions = [questions]
                for q in questions:
                    if "attributes" not in q:
                        continue
                    attributes = q.get("attributes")
                    if attribute.value not in attributes:
                        continue
                    qids.append(int(q.get("id")))
                    question_attributes.update({
                        int(q.get("id")): attributes
                    })
        question = crud_question.get_question_by_ids(
            session=session, ids=qids)
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
    question = [f.formatted_with_attributes for f in question]
    for q in question:
        key = q.get('id')
        attr = question_attributes.get(key) or []
        q['attributes'] = attr
        # number value
        numbers = []
        numb_val = answer_values.get(int(key)) or []
        count_numb = {x: numb_val.count(x) for x in numb_val}
        for val, count in count_numb.items():
            numbers.append({"value": val, "count": count})
        numbers.sort(key=lambda x: x.get('value'))
        q['number'] = numbers
    return question
