import os
import time
from typing import List
from datetime import timedelta
from db import crud_form
from db import crud_question
from db import crud_data
from db.connection import Base, SessionLocal, engine
from db.truncator import truncate
from db import crud_answer
from models.question import QuestionType
from models.answer import Answer
from models.history import History
import flow.auth as flow_auth


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()

# TODO:: MONITORING DATAPOINT
# 3. we need to seed both registration and monitoring datapoints
# (while monitoring will be have histories)


def seed_datapoint(token, data, form):
    form_id = form.id
    monitoring = True if form.registration_form else False
    formInstances = data.get('formInstances')
    nextPageUrl = data.get('nextPageUrl')
    for fi in formInstances:
        datapoint_id = fi.get('dataPointId')
        answers = []
        geoVal = None
        # check if first monitoring datapoint exist
        datapoint_exist = False
        if monitoring:
            datapoint_exist = crud_data.get_data_by_identifier(
                session=session,
                identifier=fi.get('identifier'),
                form=form_id)
        # fetching answers value into answer model
        for key, value in fi.get('responses').items():
            for val in value:
                for kval, aval in val.items():
                    question = crud_question.get_question_by_id(
                        session=session, id=kval)
                    if not question:
                        print(f"{kval}: 404 not found")
                        continue
                    if question.type == QuestionType.geo:
                        geoVal = [aval.get('lat'), aval.get('long')]
                    answer = Answer(
                        question=question.id,
                        created=fi.get('createdAt'),
                        updated=fi.get('modifiedAt'))
                    # if datapoint exist, move current answer as history
                    if datapoint_exist:
                        current_answers = \
                            crud_answer.get_answer_by_data_and_question(
                                session=session,
                                data=datapoint_exist.id,
                                questions=[question.id])
                        if len(current_answers):
                            current_answer = current_answers[0]
                            # create history
                            history = History(
                                question=question.id,
                                data=datapoint_exist.id,
                                text=current_answer.text,
                                value=current_answer.value,
                                options=current_answer.options,
                                created=current_answer.created,
                                updated=current_answer.updated)
                            # update current answer
                            update_answer = answer
                            update_answer.id = current_answer.id,
                            update_answer.data = datapoint_exist.id,
                            crud_answer.update_answer(
                                session=session, answer=update_answer,
                                history=history, type=question.type,
                                value=aval)
                            print(f"Update Datapoint {datapoint_exist.id}")
                            print(f"Update Answer {answer.id}")
                        else:
                            # add answer
                            crud_answer.add_answer(
                                session=session, answer=answer,
                                type=question.type, value=aval)
                    if not datapoint_exist:
                        answer = crud_answer.append_value(
                            answer=answer, value=aval, type=question.type)
                        answers.append(answer)
        if not datapoint_exist:
            # add new datapoint
            data = crud_data.add_data(
                session=session,
                datapoint_id=datapoint_id,
                identifier=fi.get('identifier'),
                name=fi.get('displayName'),
                form=form_id,
                registration=False if monitoring else True,
                geo=geoVal,
                created=fi.get('createdAt'),
                updated=fi.get('modifiedAt'),
                answers=answers)
            print(f"New Datapoint: {data.id}")
    print("------------------------------------------")
    if nextPageUrl:
        print("fetch next page")
        data = flow_auth.get_data(
            url=nextPageUrl, token=token)
        if len(data.get('formInstances')):
            seed_datapoint(data=data)
    print("------------------------------------------")
    print(f"{form_id}: seed complete")
    print("------------------------------------------")


def datapoint_seeder(token: dict, forms: List[dict]):
    start_time = time.process_time()

    for table in ["data", "answer", "history"]:
        action = truncate(session=session, table=table)
        print(action)

    for form in forms:
        # fetch datapoint
        form_id = form.get('id')
        survey_id = form.get('survey_id')
        check_form = crud_form.get_form_by_id(session=session, id=form_id)
        if not check_form:
            continue
        data = flow_auth.get_datapoint(
            token=token, survey_id=survey_id, form_id=form_id)
        if not data:
            print(f"{form_id}: seed ERROR!")
            break
        seed_datapoint(token=token, data=data, form=check_form)

    elapsed_time = time.process_time() - start_time
    elapsed_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
    print(f"\n-- SEED DATAPOINT DONE IN {elapsed_time}\n")
