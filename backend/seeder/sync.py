import os
import time
import flow.auth as flow_auth
from datetime import timedelta
from db.connection import Base, SessionLocal, engine
from db import crud_sync
from db import crud_data
from db import crud_question
from db import crud_answer
from db import crud_form
from models.question import QuestionType
from models.answer import Answer
from models.history import History

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()

start_time = time.process_time()


def sync(sync_data: dict):
    changes = sync_data.get('changes')
    print(changes)
    next_sync_url = sync_data.get('nextSyncUrl')
    # save next sync URL
    if next_sync_url:
        crud_sync.add_sync(session=session, url=next_sync_url)
    # manage form instance changes
    for fi in changes.get('formInstanceChanged'):
        form = crud_form.get_form_by_id(
            session=session, id=fi.get('formId'))
        if not form:
            continue
        datapoint_id = fi.get('dataPointId')
        answers = []
        geoVal = None
        monitoring = True if form.registration_form else False
        # check if monitoring datapoint exist
        datapoint_exist = False
        if monitoring:
            datapoint_exist = crud_data.get_data_by_identifier(
                session=session,
                identifier=fi.get('identifier'),
                form=form.id)
        current_data = crud_data.get_data_by_id(
            session=session, id=datapoint_id)
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
                        data=datapoint_id,
                        question=question.id,
                        created=fi.get('createdAt'))
                    # if datapoint exist, move current answer as history
                    if datapoint_exist:
                        current_answers = \
                            crud_answer.get_answer_by_data_and_question(
                                session=session,
                                data=datapoint_exist.id,
                                questions=[question.id])
                        if len(current_answers):
                            # create history and update current answer
                            current_answer = current_answers[0]
                            history = History(
                                question=question.id,
                                data=datapoint_exist.id,
                                created=current_answer.created)
                            crud_answer.update_answer(
                                session=session, answer=answer,
                                history=history, type=question.type,
                                value=aval)
                        else:
                            # add answer
                            crud_answer.add_answer(
                                session=session, answer=answer,
                                type=question.type, value=aval)
                    # update registration datapoint
                    if current_data and not datapoint_exist:
                        crud_answer.update_answer(
                            session=session, answer=answer,
                            type=question.type, value=aval)
                    if not datapoint_exist and not current_data:
                        answer = crud_answer.append_value(
                            answer=answer, value=aval, type=question.type)
                        answers.append(answer)
        if not current_data and not datapoint_exist:
            # add new datapoint
            data = crud_data.add_data(
                session=session,
                id=datapoint_id,
                identifier=fi.get('identifier'),
                name=fi.get('displayName'),
                form=form.id,
                geo=geoVal,
                created=fi.get('createdAt'),
                answers=answers)
            print(f"Sync New Datapoint: {data.id}")
            continue
        # update datapoint
        update_data = current_data
        update_data.name = fi.get('displayName'),
        update_data.form = form.id,
        update_data.geo = geoVal,
        update_data.updated = fi.get('modifiedAt'),
        updated = crud_data.update_data(session=session, data=update_data)
        print(f"Sync Update Datapoint: {updated.id}")
    # call next sync URL
    sync_data = flow_auth.get_data(url=next_sync_url, token=token)
    if sync_data:
        sync(sync_data=sync_data)


last_sync_url = crud_sync.get_last_sync(session=session)
sync_data = None
if last_sync_url:
    token = flow_auth.get_token()
    sync_data = flow_auth.get_data(
        url=last_sync_url.url, token=token)

if sync_data:
    sync(sync_data=sync_data)


elapsed_time = time.process_time() - start_time
elapsed_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
print(f"\n-- SYNC DONE IN {elapsed_time}\n")
