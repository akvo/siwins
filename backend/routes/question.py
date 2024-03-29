import os
from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from typing import List, Optional
from sqlalchemy.orm import Session
from db.crud_question import get_question, get_question_by_attributes
from db.crud_jmp import get_jmp_config
from db.crud_question_group import get_question_group_by_id
from db.crud_data import get_all_data
from db.connection import get_session
from models.question import (
    QuestionFormattedWithAttributes,
    QuestionAttributes,
    QuestionType,
)
from models.answer import Answer
from models.data import Data

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
    session: Session = Depends(get_session),
):
    jmp_categories = []
    questions = []
    # collect all question / with attributes
    if not attribute:
        question = get_question(session=session)
        question = [q.formatted_with_attributes for q in question]
    if attribute == QuestionAttributes.indicator:
        # add jmp categories into indicator questions
        jmp_configs = get_jmp_config()
        for jci, jc in enumerate(jmp_configs):
            # ** Use JMP display name instead of name
            name = jc["display_name"] if "display_name" in jc else jc["name"]
            labels = jc.get("labels")
            name_id = jc.get("name_id")
            jmp_group = jc.get("question_group")
            category_type = jc.get("category_type")
            jmp_group_name = (
                "JMP Indicator" if category_type == "jmp" else "Untitled Group"
            )
            jmp_group_order = 0
            if jmp_group:
                # get question group name
                group = get_question_group_by_id(session=session, id=jmp_group)
                group = group.only_name
                jmp_group_name = group["name"] if group else jmp_group_name
                jmp_group_order = group["order"] if group else jmp_group_name
            for lbi, lb in enumerate(labels):
                lb["order"] = lbi + 1
                lb["description"] = None
            # generate jmp categories to show as indicator
            jmp_categories.append(
                {
                    "id": f"jmp-{name_id if name else jci}",
                    "group": jmp_group_name,
                    "name": name,
                    "type": "jmp",
                    "attributes": ["indicator"],
                    "option": labels,
                    "number": [],
                    "qg_order": jmp_group_order,
                    "q_order": 0 if jmp_group else jci,
                }
            )
        # EOL add jmp categories into indicator questions
    # append jmp categories into questions
    questions += jmp_categories
    if attribute:
        question = get_question_by_attributes(
            session=session, attribute=attribute.value
        )
        # get answer number values
        number_qids = []
        for q in question:
            if q.type != QuestionType.number:
                continue
            number_qids.append(q.id)
        # only number answers from current True datapoints
        current_data_ids = get_all_data(
            session=session, columns=[Data.id], current=True
        )
        current_data_ids = [c.id for c in current_data_ids]
        answers = (
            session.query(Answer)
            .filter(Answer.data.in_(current_data_ids))
            .filter(Answer.question.in_(number_qids))
            .all()
        )
        answer_values = {}
        for a in answers:
            key = a.question
            if key not in answer_values:
                answer_values.update({key: [a.value]})
            else:
                answer_values.update({key: answer_values[key] + [a.value]})
        # EOL number values
        question = [q.formatted_with_attributes for q in question]
        # sort
        question.sort(key=lambda x: (x.get("qg_order"), x.get("q_oder")))
        for q in question:
            key = q.get("id")
            if q.get("type") != "number":
                continue
            # add umber value to question
            numbers = []
            numb_val = answer_values.get(int(key)) or []
            count_numb = {x: numb_val.count(x) for x in numb_val}
            for val, count in count_numb.items():
                numbers.append({"value": val, "count": count})
            numbers.sort(key=lambda x: x.get("value"))
            q["number"] = numbers
    # concat jmp categories indicator with question
    res = questions + question
    # reorder after concat
    res.sort(key=lambda x: (x.get("qg_order"), x.get("q_oder")))
    return res
