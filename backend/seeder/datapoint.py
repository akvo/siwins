import os
import json
import time
from typing import List
from sqlalchemy.orm import Session
from datetime import timedelta
from db import crud_form
from db import crud_question
from db import crud_data
from db import crud_answer
from models.question import QuestionType
from models.answer import Answer
from models.history import History
from models.form import Form
import flow.auth as flow_auth
from utils.mailer import send_error_email
from utils.i18n import ValidationText

from source.main import main_config
from seeder.seeder_config import (
    ENABLE_RANKING_CHECK_FOR_SAME_SCHOOL_CODE,
    ENABLE_CHECK_FOR_SAME_SCHOOL_CODE,
    ENABLE_MANUAL_SCHOOL_INFOMATION
)

DATAPOINT_PATH = main_config.DATAPOINT_PATH
MONITORING_FORM = main_config.MONITORING_FORM
MONITORING_ROUND = main_config.MONITORING_ROUND
QuestionConfig = main_config.QuestionConfig
SchoolInformationEnum = main_config.SchoolInformationEnum
CascadeLevels = main_config.CascadeLevels
SchoolTypeRanking = main_config.SchoolTypeRanking


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

year_conducted_qid = QuestionConfig.year_conducted.value
school_information_qid = QuestionConfig.school_information.value
school_type_qid = QuestionConfig.school_type.value
school_category_qid = QuestionConfig.school_category.value

school_province_enum = SchoolInformationEnum.province.value
school_type_enum = SchoolInformationEnum.school_type.value
school_name_enum = SchoolInformationEnum.school_name.value
school_code_enum = SchoolInformationEnum.school_code.value

school_province_level = (
    CascadeLevels.school_information.value[school_province_enum])
school_type_level = CascadeLevels.school_information.value[school_type_enum]
school_name_level = CascadeLevels.school_information.value[school_name_enum]
school_code_level = CascadeLevels.school_information.value[school_code_enum]

school_type_has_ranking = SchoolTypeRanking.has_ranking.value
school_type_rankings = SchoolTypeRanking.rankings.value

# Error
error = []


def seed_datapoint(session: Session, token: dict, data: dict, form: Form):
    TESTING = os.environ.get("TESTING")
    CURRENT_MONITORING_ROUND = MONITORING_ROUND
    if TESTING:
        CURRENT_MONITORING_ROUND = 2023
    form_id = form.id
    # form.registration form None by default
    monitoring = True if form.registration_form else False
    nextPageUrl = data.get("nextPageUrl")
    formInstances = data.get("formInstances")
    formInstances.sort(key=lambda fi: fi["createdAt"], reverse=False)
    for fi in formInstances:
        datapoint_id = fi.get("dataPointId")
        data_id = fi.get("id")
        answers = []
        geoVal = None
        year_conducted = None
        school_information = None
        is_error = False  # found incorrect data then skip seed/sync

        # check if first monitoring datapoint exist
        datapoint_exist = False
        if monitoring and MONITORING_FORM:
            datapoint_exist = crud_data.get_data_by_identifier(
                session=session, identifier=fi.get("identifier"), form=form_id
            )

        # BEGIN generate school information manually
        if ENABLE_MANUAL_SCHOOL_INFOMATION:
            target_questions = {}
            target_qids = [
                school_information_qid, school_type_qid, school_category_qid
            ]
            target_qids = set(map(str, target_qids))
            for group in fi.get("responses").values():
                for entry in group:
                    for question_id, answer in entry.items():
                        if question_id in target_qids:
                            target_questions[question_id] = answer

            manual_school_information = {}
            for qid in target_qids:
                res = target_questions.get(qid, None)
                if not res:
                    # There're some datapoints without school category answer
                    continue

                qid = int(qid)
                if qid == school_information_qid:
                    province = res[school_province_level]
                    province = province.get("name", None) if province else None
                    manual_school_information["province"] = province

                    s_name = res[school_name_level]
                    s_name = s_name.get("name", None) if s_name else None
                    manual_school_information["name"] = s_name

                    s_code = res[school_code_level]
                    s_code = s_code.get("name", None) if s_code else None
                    manual_school_information["code"] = s_code
                    continue

                res = res[0]
                if qid == school_type_qid:
                    s_type = res.get("text", None) if res else None
                    manual_school_information["type"] = s_type
                    continue

                if qid == school_category_qid:
                    s_cat = res.get("text", None) if res else None
                    manual_school_information["category"] = s_cat
                    continue

            if manual_school_information:
                school_information = [
                    manual_school_information.get("province"),
                    manual_school_information.get("type"),
                    manual_school_information.get("name"),
                    manual_school_information.get("code"),
                ]
                if manual_school_information.get("category"):
                    school_information.append(
                        manual_school_information.get("category"))
        # EOL generate school information manually

        # fetching answers value into answer model
        for key, value in fi.get("responses").items():
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
                    if monitoring_answer > CURRENT_MONITORING_ROUND:
                        desc = ValidationText.incorrect_monitoring_round.value
                        error.append(
                            {
                                "form_id": form_id,
                                "instance_id": data_id,
                                "answer": monitoring_answer,
                                "description": desc,
                            }
                        )
                        is_error = True
                        continue
                    # EOL check for incorrect monitoring round
                    if question.type == QuestionType.geo or question.meta_geo:
                        geoVal = [aval.get("lat"), aval.get("long")]
                    answer = Answer(
                        question=question.id,
                        created=fi.get("createdAt"),
                        updated=fi.get("modifiedAt"),
                    )
                    # Monitoring
                    # if datapoint exist, move current answer as history
                    if datapoint_exist:
                        # print(f"Update Datapoint {datapoint_exist.id}")
                        current_answers = (
                            crud_answer.get_answer_by_data_and_question(
                                session=session,
                                data=datapoint_exist.id,
                                questions=[question.id],
                            )
                        )
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
                            # print(f"Update Answer {answer.id}")
                    # new datapoint and answers
                    if not datapoint_exist:
                        answer = crud_answer.append_value(
                            answer=answer, value=aval, type=question.type
                        )
                        answers.append(answer)

                    # custom
                    if year_conducted_qid and year_conducted_qid == qid:
                        year_conducted = int(answer.options[0])
                    if (
                        school_information_qid
                        and school_information_qid == qid
                        and not ENABLE_MANUAL_SCHOOL_INFOMATION
                    ):
                        school_information = answer.options
                    # EOL custom

        # check if school_information is not defined
        if not school_information:
            desc = ValidationText.school_information_is_not_defined.value
            error.append(
                {
                    "form_id": form_id,
                    "instance_id": data_id,
                    "answer": f"NULL - {year_conducted}",
                    "description": desc,
                }
            )
            is_error = True
        # EOL check if school_information is not defined

        school_code = (
            school_information[school_code_level]
            if school_code_level < len(school_information)
            else None
        )

        # do not include school with code "not available"
        if school_code and school_code.lower() == "not available":
            # set error message
            prev_instance = "-"
            school_answer = "|".join(school_information)
            desc = ValidationText.school_code_not_available_ignored.value
            desc = f"{desc} - prev instance_id: {prev_instance}"
            error.append(
                {
                    "form_id": form_id,
                    "instance_id": data_id,
                    "answer": f"{school_answer} - {year_conducted}",
                    "description": desc,
                }
            )
            is_error = True
            continue
        # EOL do not include school with code "not available"

        # check if school type (in school information) has ranking
        is_school_type_has_ranking = False
        if (
            school_information and school_information[school_type_level] and
            ENABLE_RANKING_CHECK_FOR_SAME_SCHOOL_CODE
        ):
            school_type = school_information[school_type_level]
            school_type = school_type.split(" ")[0]
            school_type = school_type.lower() if school_type else None
            is_school_type_has_ranking = school_type in school_type_has_ranking
        # EOL check if school type (in school information) has ranking

        # check datapoint with same school code and monitoring round
        check_same_school_code_and_monitoring = None
        if (
            is_school_type_has_ranking and year_conducted and
            ENABLE_RANKING_CHECK_FOR_SAME_SCHOOL_CODE
        ):
            check_same_school_code_and_monitoring = (
                crud_data.get_data_by_school_code(
                    session=session,
                    school_code=school_code,
                    year_conducted=year_conducted,
                )
            )

        if (
            check_same_school_code_and_monitoring
            and school_code
            and school_code.lower() != "not available"
        ):
            # check school type ranking to decide the data seed
            if ENABLE_RANKING_CHECK_FOR_SAME_SCHOOL_CODE:
                prev_school_information = (
                    check_same_school_code_and_monitoring.school_information
                )
                prev_school_type = prev_school_information[school_type_level]
                prev_school_type = prev_school_type.split(" ")[0]
                prev_school_type = (
                    prev_school_type.lower() if prev_school_type else None
                )
                prev_school_type_ranking = (
                    school_type_rankings[prev_school_type]
                )

                school_type = school_information[school_type_level]
                school_type = school_type.split(" ")[0]
                school_type = school_type.lower() if school_type else None
                school_type_ranking = school_type_rankings[school_type]

                if school_type_ranking > prev_school_type_ranking:
                    # use new answers to replace the prev answer
                    # delete prev datapoint
                    crud_data.delete_by_id(
                        session=session,
                        id=check_same_school_code_and_monitoring.id,
                    )

                if school_type_ranking <= prev_school_type_ranking:
                    # set error message
                    prev_instance = check_same_school_code_and_monitoring.id
                    school_answer = "|".join(school_information)
                    desc = (
                        ValidationText.school_same_type_code_monitoring_exist
                    )
                    desc = desc.value
                    desc = f"{desc} - prev instance_id: {prev_instance}"
                    error.append(
                        {
                            "form_id": form_id,
                            "instance_id": data_id,
                            "answer": f"{school_answer} - {year_conducted}",
                            "description": desc,
                        }
                    )
                    is_error = True
                # EOL check school type ranking to decide the data seed

        # EOL check datapoint with same school code and monitoring round

        # check datapoint with same school and monitoring round
        check_same_school_and_monitoring = None
        if (
            year_conducted and school_information and
            ENABLE_CHECK_FOR_SAME_SCHOOL_CODE
        ):
            check_same_school_and_monitoring = crud_data.get_data_by_school(
                session=session,
                schools=school_information,
                year_conducted=year_conducted,
            )
        if (
            check_same_school_and_monitoring and
            ENABLE_CHECK_FOR_SAME_SCHOOL_CODE
        ):
            prev_instance = check_same_school_and_monitoring.id
            school_answer = "|".join(school_information)
            desc = ValidationText.school_monitoring_exist.value
            desc = f"{desc} - prev instance_id: {prev_instance}"
            error.append(
                {
                    "form_id": form_id,
                    "instance_id": data_id,
                    "answer": f"{school_answer} - {year_conducted}",
                    "description": desc,
                }
            )
            is_error = True
        # EOL check datapoint with same school and monitoring round

        if is_error:
            # skip seed/sync when error
            continue

        # check for current datapoint
        current_datapoint = True
        check_datapoint = crud_data.get_data_by_school(
            session=session, schools=school_information
        )
        # update prev datapoint with same school to current False
        update_prev_datapoint_current_flag = (
            check_datapoint
            and check_datapoint.year_conducted != int(year_conducted)
        )
        if update_prev_datapoint_current_flag:
            # check current flag value
            # check_datapoint.year_conducted ==> previous data monitoring year
            # int(year_conducted) ==> current data monitoring year
            current_datapoint = (
                True
                if check_datapoint.year_conducted < int(year_conducted)
                else False
            )
            check_datapoint.current = not current_datapoint
            crud_data.update_data(session=session, data=check_datapoint)
        # EOL check for current datapoint

        # add new datapoint
        if answers:
            data = crud_data.add_data(
                id=data_id,
                session=session,
                datapoint_id=datapoint_id,
                identifier=fi.get("identifier"),
                name=fi.get("displayName"),
                form=form_id,
                registration=False if monitoring else True,
                geo=geoVal,
                created=fi.get("createdAt"),
                updated=fi.get("modifiedAt"),
                answers=answers,
                year_conducted=year_conducted,
                school_information=school_information,
                current=current_datapoint,
            )
        # print(f"New Datapoint: {data.id}")
    # print("------------------------------------------")
    if not TESTING and nextPageUrl:
        data = flow_auth.get_data(url=nextPageUrl, token=token)
        if data and len(data.get("formInstances")):
            seed_datapoint(session=session, token=token, data=data, form=form)
    print("------------------------------------------")
    print(f"Datapoints for {form_id}: seed complete")
    print("------------------------------------------")


def datapoint_seeder(session: Session, token: dict, forms: List[dict]):
    TESTING = os.environ.get("TESTING")
    start_time = time.process_time()

    for form in forms:
        # fetch datapoint
        form_id = form.get("id")
        survey_id = form.get("survey_id")
        check_form = crud_form.get_form_by_id(session=session, id=form_id)
        if not check_form:
            continue
        if TESTING:
            data_file = f"{DATAPOINT_PATH}/{form_id}_data.json"
            data = {}
            with open(data_file) as json_file:
                data = json.load(json_file)
        if not TESTING:
            data = flow_auth.get_datapoint(
                token=token, survey_id=survey_id, form_id=form_id
            )
        if not data:
            print(f"{form_id}: seed ERROR!")
            break
        seed_datapoint(
            session=session, token=token, data=data, form=check_form
        )

    if error:
        # send error after sync completed
        send_error_email(error=error, filename="error-seed")

    elapsed_time = time.process_time() - start_time
    elapsed_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
    print(f"\n-- SEED DATAPOINT DONE IN {elapsed_time}\n")
