# README
# data sync only support for datapoint change/delete

import os
import flow.auth as flow_auth
from sqlalchemy.orm import Session
from sqlalchemy import exc
from db import crud_sync
from db import crud_data
from db import crud_question
from db import crud_answer
from db import crud_form
from models.question import QuestionType
from models.answer import Answer
from models.history import History, HistoryDict
from models.data import Data
from typing import List
from source.main_config import (
    MONITORING_FORM, QuestionConfig,
    MONITORING_ROUND
)
from utils.mailer import send_error_email

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

year_conducted_qid = QuestionConfig.year_conducted.value
school_information_qid = QuestionConfig.school_information.value

# Error
error = []


def delete_current_data_monitoring(
    session: Session,
    data: int,
    lh: List[HistoryDict],
) -> None:
    delete_error = []
    """
    get the last history as a replacement for current data monitoring
    """
    for history in lh:
        try:
            with session.begin_nested():
                crud_answer.update_answer_from_history(
                    session=session, data=data, history=history
                )
        except exc.IntegrityError:
            delete_error.push(history)
    session.commit()
    if len(delete_error):
        for err in delete_error:
            print(f"Error | Delete Datapoint History: {err.id}")
    else:
        print(f"Success | Delete Datapoint: {data}")


def delete_registration_items(session: Session, items: List[Data]) -> None:
    for item in items:
        crud_data.delete_by_id(session=session, id=item.id)
        print(f"Success| Delete Datapoint: {item.id}")


def deleted_data_sync(session: Session, data: list) -> None:
    for d in data:
        dp = crud_data.get_data_by_id(session=session, id=d)
        if dp:
            if dp.registration:
                monitoring = crud_data.get_monitoring_data(
                    session=session, identifier=dp.identifier
                )
                items = [dp]
                if monitoring:
                    items += monitoring
                delete_registration_items(session=session, items=items)
            else:
                lh = crud_data.get_last_history(
                    session=session, datapoint_id=dp.datapoint_id, id=dp.id
                )
                if len(lh):
                    delete_current_data_monitoring(
                        session=session, data=dp.id, lh=lh
                    )
                else:
                    crud_data.delete_by_id(session=session, id=dp.id)
                    print(f"Success| Delete Datapoint: {dp.id}")


def data_sync(
    token: dict,
    session: Session,
    sync_data: dict
):
    TESTING = os.environ.get("TESTING")
    # TODO:: Support other changes from FLOW API
    print("------------------------------------------")
    changes = sync_data.get("changes")
    # handle on sync deleted data monitoring
    deleted_items = changes.get("formInstanceDeleted")
    if len(deleted_items):
        deleted_data_sync(session=session, data=deleted_items)
    # next sync URL
    next_sync_url = sync_data.get("nextSyncUrl")
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
        # data point loop
        form = crud_form.get_form_by_id(session=session, id=fi.get("formId"))
        if not form:
            continue

        datapoint_id = fi.get("dataPointId")
        data_id = fi.get("id")
        answers = []
        geoVal = None
        year_conducted = None
        school_information = None
        is_error = False  # found incorrect data then skip seed/sync

        # check if monitoring datapoint exist
        # form.registration form None by default
        monitoring = True if form.registration_form else False
        datapoint_exist = False
        if monitoring and MONITORING_FORM:
            datapoint_exist = crud_data.get_data_by_identifier(
                session=session, identifier=fi.get("identifier"), form=form.id
            )
        # updated data to check if current datapoint exist
        updated_data = crud_data.get_data_by_id(session=session, id=data_id)
        # fetching answers value into answer model
        for key, value in fi.get("responses").items():
            # response / answer loop
            for val in value:
                for kval, aval in val.items():
                    # info: kval = question id
                    # info: aval = answer
                    qid = int(kval)
                    question = crud_question.get_question_by_id(
                        session=session, id=kval
                    )
                    if not question:
                        print(f"{kval}: 404 not found")
                        continue
                    # check for incorrect monitoring round
                    monitoring_answer = 0
                    if qid == QuestionConfig.year_conducted.value:
                        monitoring_answer = int(aval[0].get("text"))
                    if monitoring_answer > MONITORING_ROUND:
                        error.append({
                            "instance_id": data_id,
                            "answer": monitoring_answer,
                            "type": "incorrect_monitoring_round"
                        })
                        is_error = True
                        continue
                    # EOL check for incorrect monitoring round
                    if question.type == QuestionType.geo:
                        geoVal = [aval.get("lat"), aval.get("long")]
                    # create answer
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

                        # custom
                        if year_conducted_qid and year_conducted_qid == qid:
                            year_conducted = answer.options[0]
                        if school_information_qid and \
                                school_information_qid == qid:
                            school_information = answer.options
                        # EOL custom

                    # new datapoint and answers
                    if not datapoint_exist and not updated_data:
                        answer = crud_answer.append_value(
                            answer=answer, value=aval, type=question.type
                        )
                        answers.append(answer)

                        # custom
                        if year_conducted_qid and year_conducted_qid == qid:
                            year_conducted = answer.options[0]
                        if school_information_qid and \
                                school_information_qid == qid:
                            school_information = answer.options
                        # EOL custom

        if is_error:
            # skip seed/sync when error
            continue

        # check for current datapoint
        current_datapoint = True
        check_datapoint = crud_data.get_data_by_school(
            session=session, schools=school_information)
        # update prev datapoint with same school to current False
        if check_datapoint:
            check_datapoint.current = False
            crud_data.update_data(
                session=session, data=check_datapoint)
        # EOL check for current datapoint

        if not updated_data and not datapoint_exist or answers:
            # add new datapoint
            data = crud_data.add_data(
                id=data_id,
                session=session,
                datapoint_id=datapoint_id,
                identifier=fi.get("identifier"),
                name=fi.get("displayName"),
                form=form.id,
                registration=False if monitoring else True,
                geo=geoVal,
                created=fi.get("createdAt"),
                answers=answers,
                year_conducted=year_conducted,
                school_information=school_information,
                current=current_datapoint
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
            # custom
            if year_conducted:
                update_data.year_conducted = year_conducted
            if school_information:
                update_data.school_information = school_information
            if check_datapoint:
                update_data.current = False
            # EOL custom
            updated = crud_data.update_data(session=session, data=update_data)
            print(f"Sync | Update Datapoint: {updated.id}")
            continue
    print("------------------------------------------")
    # save next sync URL
    if next_sync_url:
        crud_sync.add_sync(session=session, url=next_sync_url)
    # call next sync URL
    sync_data = []
    if not TESTING:
        sync_data = flow_auth.get_data(url=next_sync_url, token=token)
    if sync_data:
        data_sync(
            token=token,
            session=session,
            sync_data=sync_data,
        )
    if not error:
        return None
    # send error after sync completed
    send_error_email(error=error, filename="error-sync")
    return error
