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
import flow.auth as flow_auth

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_source = "./source/static"


def form_seeder(session: Session, token: dict, forms: List[dict]):
    TESTING = os.environ.get("TESTING")
    start_time = time.process_time()

    for form in forms:
        # fetch form
        form_id = form.get('id')
        if TESTING:
            form_file = f"{test_source}/{form_id}_form.json"
            json_form = {}
            with open(form_file) as json_file:
                json_form = json.load(json_file)
        if not TESTING:
            json_form = flow_auth.get_form(token=token, form_id=form_id)

        name = json_form.get('name') \
            if 'name' in json_form else form.get('name')
        version = json_form.get('version') if 'version' in json_form else 1.0
        form = crud_form.add_form(
            session=session,
            name=name,
            id=json_form.get('surveyId'),
            registration_form=form.get('registration_form'),
            version=version,
            description=json_form.get('description'))
        print(f"Form: {form.name}")

        questionGroups = json_form.get('questionGroup')
        if isinstance(questionGroups, dict):
            questionGroups = [questionGroups]
        for qg in questionGroups:
            question_group = crud_question_group.add_question_group(
                session=session,
                name=qg.get('heading'),
                form=form.id,
                description=qg.get('description'),
                repeatable=True if qg.get('repeatable') else False)
            print(f"Question Group: {question_group.name}")

            questions = qg.get('question')
            if isinstance(questions, dict):
                questions = [questions]
            for i, q in enumerate(questions):
                # handle question type
                type = q.get('type')
                validationType = None
                allowMultiple = q.get('allowMultiple')
                if 'validationRule' in q:
                    vr = q.get('validationRule')
                    validationType = vr.get('validationType')
                if type == 'free' and not validationType:
                    type = QuestionType.text.value
                if type == 'free' and validationType == 'numeric':
                    type = QuestionType.number.value
                if type == 'option' and allowMultiple:
                    type == QuestionType.multiple_option.value
                meta_geo = q.get('localeLocationFlag')
                question = crud_question.add_question(
                    session=session,
                    name=q.get('text'),
                    id=q.get('id') if "id" in q else None,
                    form=form.id,
                    question_group=question_group.id,
                    type=type,
                    meta=q.get("localeNameFlag"),
                    meta_geo=meta_geo if meta_geo else False,
                    order=q.get('order'),
                    required=q.get('mandatory'),
                    dependency=q["dependency"] if "dependency" in q else None,
                    option=[])
                print(f"{i}.{question.name}")
        print("------------------------------------------")

    elapsed_time = time.process_time() - start_time
    elapsed_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
    print(f"\n-- SEED FORM DONE IN {elapsed_time}\n")
