import os
import json
import time
from typing import List
from sqlalchemy.orm import Session
from datetime import timedelta
from db import crud_form
from db import crud_question_group
from db import crud_question
from models.question import QuestionType
from source.main_config import FORM_PATH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def form_seeder(session: Session, forms: List[dict]):
    TESTING = os.environ.get("TESTING")
    start_time = time.process_time()

    for form in forms:
        # fetch form
        form_id = form.get("id")
        if TESTING:
            form_file = f"{FORM_PATH}/{form_id}.json"

        if not TESTING:
            form_file = f"{FORM_PATH}/{form_id}.json"

        json_form = {}
        with open(form_file) as json_file:
            json_form = json.load(json_file)

        form_name = form.get("name")
        name = json_form.get("name") if "name" in json_form else form_name
        version = json_form.get("version") if "version" in json_form else 1.0
        form = crud_form.add_form(
            session=session,
            name=name,
            id=json_form.get("surveyId"),
            registration_form=form.get("registration_form"),
            version=version,
            description=json_form.get("description"),
        )
        print(f"Form: {form.name}")

        questionGroups = json_form.get("questionGroup")
        if isinstance(questionGroups, dict):
            questionGroups = [questionGroups]
        for qg in questionGroups:
            question_group = crud_question_group.add_question_group(
                session=session,
                name=qg.get("heading"),
                form=form.id,
                description=qg.get("description"),
                repeatable=True if qg.get("repeatable") else False,
            )
            # print(f"Question Group: {question_group.name}")

            questions = qg.get("question")
            if isinstance(questions, dict):
                questions = [questions]
            for i, q in enumerate(questions):
                meta_geo = q.get("localeLocationFlag")
                # handle question type
                type = q.get("type")
                validationType = None
                if "validationRule" in q:
                    vr = q.get("validationRule")
                    validationType = vr.get("validationType")
                if type == "free" and not validationType:
                    type = QuestionType.text.value
                if type == "free" and validationType == "numeric":
                    type = QuestionType.number.value
                if type == "option" and "option" in q:
                    allowMultiple = q["options"].get("allowMultiple")
                    type == QuestionType.multiple_option.value \
                        if allowMultiple else type
                # EOL handle question type
                dependency = None
                if "dependency" in q:
                    dependency = [q["dependency"]]
                attributes = None
                if "attributes" in q:
                    attributes = q["attributes"]
                display_name = None
                if "display_name" in q:
                    display_name = q["display_name"]
                options = []
                if "options" in q:
                    options = q["options"].get("option") or []
                # question
                crud_question.add_question(
                    session=session,
                    name=q.get("text"),
                    id=q.get("id") if "id" in q else None,
                    form=form.id,
                    question_group=question_group.id,
                    type=type,
                    meta=q.get("localeNameFlag"),
                    meta_geo=meta_geo if meta_geo else False,
                    order=q.get("order"),
                    required=q.get("mandatory"),
                    dependency=dependency,
                    option=options,
                    attributes=attributes,
                    display_name=display_name
                )
                # print(f"{i}.{question.name}")
        print("------------------------------------------")

    elapsed_time = time.process_time() - start_time
    elapsed_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
    print(f"\n-- SEED FORM DONE IN {elapsed_time}\n")
