import os
import flow.auth as flow_auth
from sqlalchemy.orm import Session
from db import crud_sync
from db import crud_data
from db import crud_question
from db import crud_answer
from db import crud_form
from models.question import QuestionType
from models.answer import Answer
from models.history import History

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def data_sync(token: dict, session: Session, sync_data: dict):
    TESTING = os.environ.get("TESTING")
    # TODO:: Support other changes from FLOW API
    print("------------------------------------------")
    changes = sync_data.get("changes")
    next_sync_url = sync_data.get("nextSyncUrl")
    # save next sync URL
    if next_sync_url:
        crud_sync.add_sync(session=session, url=next_sync_url)
    # manage deleted datapoint
    if changes.get("dataPointDeleted"):
        deleted_data_ids = [
            int(dpid) for dpid in changes.get("dataPointDeleted")
        ]
        crud_data.delete_bulk(session=session, ids=deleted_data_ids)
        print(f"Sync | Delete Datapoints: {deleted_data_ids}")
    # manage form instance changes
    # sort form instances by createdAt
    formInstances = changes.get("formInstanceChanged")
    formInstances.sort(key=lambda fi: fi["createdAt"], reverse=False)
    for fi in formInstances:
        form = crud_form.get_form_by_id(session=session, id=fi.get("formId"))
        if not form:
            continue
        datapoint_id = fi.get("dataPointId")
        data_id = fi.get("id")
        answers = []
        geoVal = None
        monitoring = True if form.registration_form else False
        # check if monitoring datapoint exist
        datapoint_exist = False
        if monitoring:
            datapoint_exist = crud_data.get_data_by_identifier(
                session=session, identifier=fi.get("identifier"), form=form.id
            )
        updated_data = crud_data.get_data_by_id(session=session, id=data_id)
        # fetching answers value into answer model
        for key, value in fi.get("responses").items():
            for val in value:
                for kval, aval in val.items():
                    question = crud_question.get_question_by_id(
                        session=session, id=kval
                    )
                    if not question:
                        print(f"{kval}: 404 not found")
                        continue
                    if question.type == QuestionType.geo:
                        geoVal = [aval.get("lat"), aval.get("long")]
                    answer = Answer(
                        question=question.id,
                        created=fi.get("createdAt"),
                    )
                    # Monitoring
                    # if datapoint exist, move current answer as history
                    if datapoint_exist:
                        print(f"Sync | Update Datapoint {datapoint_exist.id}")
                        current_answers = (
                            crud_answer.get_answer_by_data_and_question(
                                session=session,
                                data=datapoint_exist.id,
                                questions=[question.id],
                            )
                        )
                        # check if history need to update
                        current_history = None
                        if updated_data:
                            current_history = (
                                crud_answer.get_history_by_data_and_question(
                                    session=session,
                                    data=data_id,
                                    questions=[question.id],
                                )
                            )
                        # answer
                        if updated_data and current_answers:
                            # handle sync updated monitoring data
                            current_answer = current_answers[0]
                            update_answer = answer
                            update_answer.id = (current_answer.id,)
                            update_answer.data = (datapoint_exist.id,)
                            crud_answer.update_answer(
                                session=session,
                                answer=update_answer,
                                type=question.type,
                                value=aval,
                            )
                        # history
                        if updated_data and current_history:
                            # handle sync updated history of monitoring data
                            current_history = current_history[0]
                            update_history = History(
                                data=data_id,
                                question=question.id,
                                created=fi.get("createdAt"),
                            )
                            update_history.id = (current_history.id,)
                            update_history.data = (updated_data.id,)
                            crud_answer.update_history(
                                session=session,
                                history=update_history,
                                type=question.type,
                                value=aval,
                            )
                        # new answer and move current answer to history
                        if not updated_data and len(current_answers):
                            current_answer = current_answers[0]
                            # create history
                            history = History(
                                question=question.id,
                                data=datapoint_exist.id,
                                text=current_answer.text,
                                value=current_answer.value,
                                options=current_answer.options,
                                created=current_answer.created,
                                updated=current_answer.updated,
                            )
                            # add history
                            crud_answer.add_history(
                                session=session, history=history
                            )
                            # delete current answer and add new answer
                            crud_answer.delete_answer_by_id(
                                session=session, id=current_answer.id
                            )
                            answer = crud_answer.append_value(
                                answer=answer, value=aval, type=question.type
                            )
                            answers.append(answer)
                        if not len(current_answers):
                            # add answer
                            new_answer = answer
                            new_answer.data = datapoint_exist.id
                            crud_answer.add_answer(
                                session=session,
                                answer=new_answer,
                                type=question.type,
                                value=aval,
                            )
                            # print(f"Sync | New Answer {answer.id}")
                    # Registration
                    # update registration datapoint
                    if updated_data and not datapoint_exist:
                        current_answers = (
                            crud_answer.get_answer_by_data_and_question(
                                session=session,
                                data=updated_data.id,
                                questions=[question.id],
                            )
                        )
                        current_answer = current_answers[0]
                        update_answer = answer
                        update_answer.id = current_answer.id
                        update_answer.data = current_answer.data
                        update_answer.created = current_answer.created
                        update_answer.updated = fi.get("modifiedAt")
                        crud_answer.update_answer(
                            session=session,
                            answer=update_answer,
                            type=question.type,
                            value=aval,
                        )
                    # new datapoint and answers
                    if not datapoint_exist and not updated_data:
                        answer = crud_answer.append_value(
                            answer=answer, value=aval, type=question.type
                        )
                        answers.append(answer)
        if not updated_data and not datapoint_exist or answers:
            # add new datapoint
            data = crud_data.add_data(
                id=fi.get("id"),
                session=session,
                datapoint_id=datapoint_id,
                identifier=fi.get("identifier"),
                name=fi.get("displayName"),
                form=form.id,
                registration=False if monitoring else True,
                geo=geoVal,
                created=fi.get("createdAt"),
                answers=answers,
            )
            print(f"Sync | New Datapoint: {data.id}")
            continue
        if updated_data:
            # update datapoint
            update_data = updated_data
            update_data.name = fi.get("displayName")
            update_data.form = form.id
            update_data.geo = geoVal
            update_data.updated = fi.get("modifiedAt")
            updated = crud_data.update_data(session=session, data=update_data)
            print(f"Sync | Update Datapoint: {updated.id}")
            continue
    print("------------------------------------------")
    # call next sync URL
    if TESTING:
        return True
    sync_data = flow_auth.get_data(url=next_sync_url, token=token)
    if sync_data:
        data_sync(token=token, session=session, sync_data=sync_data)
