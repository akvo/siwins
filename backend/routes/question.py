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
from models.question import QuestionAttributes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source = "./source/static"

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
        forms = crud_form.get_form(session=session)
        for f in forms:
            form_file = f"{source}/{f.id}_form.json"
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
                        q.get("id"): attributes
                    })
        question = crud_question.get_question_by_ids(
            session=session, ids=qids)
    question = [f.formatted_with_attributes for f in question]
    for q in question:
        key = str(q.get('id'))
        attr = question_attributes.get(key) or []
        q['attributes'] = attr
    return question
