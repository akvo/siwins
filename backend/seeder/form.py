import os
import time
from typing import List
from datetime import timedelta
from db import crud_form
from db import crud_question_group
from db import crud_question
from db.truncator import truncate
from db.connection import Base, SessionLocal, engine
from models.question import QuestionType
import flow.auth as flow_auth

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()


def form_seeder(token: dict, forms: List[dict]):
    start_time = time.process_time()

    for table in ["form", "question_group", "question", "option"]:
        action = truncate(session=session, table=table)
        print(action)

    for form in forms:
        # fetch form
        form_id = form.get('id')
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
                question = crud_question.add_question(
                    session=session,
                    name=q.get('text'),
                    id=q.get('id') if "id" in q else None,
                    form=form.id,
                    question_group=question_group.id,
                    type=type,
                    meta=q.get("localeNameFlag"),
                    order=q.get('order'),
                    required=q.get('mandatory'),
                    dependency=q["dependency"] if "dependency" in q else None,
                    option=[])
                print(f"{i}.{question.name}")
        print("------------------------------------------")

    elapsed_time = time.process_time() - start_time
    elapsed_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
    print(f"\n-- SEED FORM DONE IN {elapsed_time}\n")
