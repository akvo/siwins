import os
import sys
import time
import json
import pandas as pd
import random
from typing import Optional, List
from datetime import datetime
from faker import Faker
from db import crud_form, crud_data, crud_option, \
    crud_question, crud_cascade
from models.question import QuestionType
from models.answer import Answer
from models.data import Data
from db.connection import Base, SessionLocal, engine
from source.geoconfig import GeoLevels
from seeder.fake_history import generate_fake_history
from db.truncator import truncate_datapoint
from utils.functions import refresh_materialized_data
from source.main_config import CLASS_PATH, TOPO_JSON_PATH, \
    ADMINISTRATION_PATH, MONITORING_FORM
from source.main_config import QuestionConfig, CascadeLevels

start_time = time.process_time()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()

config = GeoLevels[CLASS_PATH].value
levels = [c["name"] for c in config]

source_geo = TOPO_JSON_PATH
fake_geolocations_file = f"{ADMINISTRATION_PATH}/fake-geolocations.csv"
fake_geolocations = os.path.exists(fake_geolocations_file)

sample_geo = False
if fake_geolocations:
    sample_geo = pd.read_csv(fake_geolocations_file)
    sample_geo = sample_geo.sample(frac=1)
    sample_geo = sample_geo.to_dict("records")
else:
    print(f"{fake_geolocations_file} is required")
    sys.exit()

with open(source_geo, "r") as geo:
    geo = json.load(geo)
    ob = geo["objects"]
    ob_name = list(ob)[0]

parent_administration = set(
    [
        d[levels[len(levels) - 1 or 0]]
        for d in [p["properties"] for p in ob[ob_name]["geometries"]]
    ]
)
forms = crud_form.get_form(session=session)
forms = [f.id for f in forms]

DEFAULT_NUMBER_OF_SEEDER = 10
repeats = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_NUMBER_OF_SEEDER

# year conducted
year_conducted_value = []
year_conducted_qid = QuestionConfig.year_conducted.value
question = crud_question.get_question_by_id(
    session=session, id=year_conducted_qid)
if question and question.type in [
    QuestionType.option,
    QuestionType.multiple_option,
]:
    year_conducted_value = crud_option.get_option_by_question_id(
        session=session, question=question.id)
    year_conducted_value = [int(v.name) for v in year_conducted_value]
    year_conducted_value = list(set(year_conducted_value))  # ordering, unique
# support other type?

# school information cascade
school_information_value = []
school_information_qid = QuestionConfig.school_information.value
question = crud_question.get_question_by_id(
    session=session, id=school_information_qid)
if question.type == QuestionType.cascade:
    school_information_value = crud_cascade.get_cascade_by_question_id(
        session=session, question=school_information_qid, level=0)
# support other type?

# setup FAKER
fake = Faker()
# TRUNCATE datapoints before running faker
truncate_datapoint(session=session)


def generate_school_information():
    cascade_answers = []
    cascade_levels = CascadeLevels.school_information.value
    prev_choice = None
    for name, level in cascade_levels.items():
        if level == 0:
            prev_choice = random.choice(
                school_information_value)
            cascade_answers.append(prev_choice)
            continue
        child = crud_cascade.get_cascade_by_parent(
            session=session,
            parent=prev_choice.id,
            level=level)
        prev_choice = random.choice(child)
        cascade_answers.append(prev_choice)
    cascade_answers = [c.name for c in cascade_answers]
    # check if that school exist in same year
    check = crud_data.get_data_by_school(
        session=session,
        schools=cascade_answers)
    if check:
        return generate_school_information()
    # EOL check if that school exist in same year
    return cascade_answers


def seed_fake_datapoint(
    form: int,
    registration: Optional[bool] = True,
    school_information: Optional[List[str]] = None,
    # default use first index of year conducted options value
    year_conducted: Optional[int] = None,
    # current data
    prev_data: Optional[Data] = None
):
    answers = []
    names = []
    iloc = i % (len(sample_geo) - 1)
    geo = sample_geo[iloc]

    # get form from database
    form = crud_form.get_form_by_id(session=session, id=form)

    # if monitoring survey available
    monitoring = None
    datapoint = None
    if MONITORING_FORM:
        monitoring = True if form.registration_form is not None else False
        datapoint = (
            crud_data.get_registration_only(session=session)
            if monitoring
            else None
        )
    # EOL if monitoring survey available

    current_answers = {}
    # custom year conducted & school information
    data_year_conducted = None
    data_school_information = None

    # iterate group and question
    for qg in form.question_group:
        for q in qg.question:
            # dependency checker, ONLY support single dependency
            if q.dependency:
                current_dependency = q.dependency[0]
                cd_question = int(current_dependency['question'])
                cd_answer = current_dependency['answer-value'].lower()
                # check answer
                dependency_answer = current_answers.get(
                    cd_question).lower() if current_answers.get(
                        cd_question) else None
                if dependency_answer != cd_answer:
                    # don't answer the question
                    continue
            # EOL dependency checker
            answer = Answer(question=q.id, created=datetime.now())
            current_answer_value = None

            # Year conducted question check
            if not MONITORING_FORM and q.id == year_conducted_qid \
                    and year_conducted_value:
                fa = year_conducted_value[0] if \
                    not year_conducted else year_conducted
                current_answer_value = "|".join([str(fa)])
                answer.options = [fa]
                if q.meta:
                    names.append(fa)
                data_year_conducted = fa
                # update current answers to check dependency
                current_answers.update({q.id: current_answer_value})
                # update answers value to seed
                answers.append(answer)
                continue
            # EOL Year conducted question check

            # School information cascade check
            if not MONITORING_FORM and q.id == school_information_qid \
                    and school_information_value:
                cascade_answers = [] if not school_information \
                    else school_information
                # random choice of school information cascade
                if not cascade_answers:
                    cascade_answers = generate_school_information()
                # EOL random choice of school information cascade
                current_answer_value = "|".join(cascade_answers)
                answer.options = cascade_answers
                if q.meta:
                    names += cascade_answers
                data_school_information = cascade_answers
                # update current answers to check dependency
                current_answers.update({q.id: current_answer_value})
                # update answers value to seed
                answers.append(answer)
                continue
            # EOL School information cascade check

            if q.type in [
                QuestionType.option,
                QuestionType.multiple_option,
            ]:
                options = crud_option.get_option_by_question_id(
                    session=session, question=q.id
                )
                fa = random.choice(options)
                current_answer_value = "|".join([fa.name])
                answer.options = [fa.name]
                if q.meta:
                    names.append(
                        datapoint.name
                        if monitoring and datapoint
                        else fa.name
                    )

            if q.type == QuestionType.number:
                fa = fake.random_int(min=10, max=50)
                current_answer_value = fa
                answer.value = current_answer_value

            if q.type == QuestionType.date:
                fa = fake.date_this_century()
                fm = fake.random_int(min=11, max=12)
                fd = fa.strftime("%d")
                current_answer_value = f"2019-{fm}-{fd}"
                answer.text = current_answer_value

            if q.type == QuestionType.geo and geo:
                current_answer_value = ("{}|{}").format(
                    geo["lat"], geo["long"])
                answer.text = current_answer_value

            if q.type == QuestionType.photo:
                current_answer_value = json.dumps({
                    'filename': fake.image_url()})
                answer.text = current_answer_value

            if q.type == QuestionType.text:
                fa = fake.company()
                current_answer_value = fa
                answer.text = current_answer_value
                if q.meta:
                    names.append(current_answer_value)

            if q.type == QuestionType.cascade:
                cascades = [geo.get(key) for key in levels]
                current_answer_value = cascades
                answer.options = current_answer_value
                if q.meta:
                    names += cascades
            # update current answers to check dependency
            current_answers.update({q.id: current_answer_value})
            # update answers value to seed
            answers.append(answer)

    # check current data
    current_datapoint = True
    if prev_data:
        check_datapoint = crud_data.get_data_by_school(
            session=session,
            schools=prev_data.school_information,
            year_conducted=prev_data.year_conducted)
        # update prev datapoint with same school to current False
        if check_datapoint:
            check_datapoint.current = False
            crud_data.update_data(
                session=session, data=check_datapoint)
    # EOL current_datapoint

    # preparing data value
    displayName = " - ".join(names) or "Untitled"
    geoVal = [geo.get("lat"), geo.get("long")]
    identifier = "-".join(fake.uuid4().split("-")[1:4])
    # add new datapoint
    data = crud_data.add_data(
        datapoint_id=datapoint.id if datapoint else None,
        identifier=datapoint.identifier if datapoint else identifier,
        session=session,
        name=displayName,
        form=form.id,
        registration=False if monitoring else True,
        geo=geoVal if not monitoring else None,
        created=datetime.now(),
        answers=answers,
        year_conducted=data_year_conducted,
        school_information=data_school_information,
        current=current_datapoint
    )
    return data


# registration data
for i in range(repeats):
    for form in forms:
        seed_fake_datapoint(form=form)


# support registration - monitoring seeder
if not MONITORING_FORM and year_conducted_qid and year_conducted_value:
    # iterate for remain year conducted value (eliminate first year)
    registration_year = year_conducted_value[0]
    datapoints = crud_data.get_data_by_year_conducted(
        session=session, year_conducted=registration_year)
    year_conducted_value = year_conducted_value[1:]
    for year in year_conducted_value:
        for d in datapoints:
            seed_fake_datapoint(
                form=d.form,
                year_conducted=year,
                school_information=d.school_information,
                prev_data=d
            )

# populate data monitoring history if monitoring survey available
if MONITORING_FORM:
    data_monitoring = crud_data.get_all_data(
        session=session, registration=False)
    for dm in data_monitoring:
        generate_fake_history(session=session, datapoint=dm)
# EOL if monitoring survey available

# refresh materialized view
refresh_materialized_data()
print(f"Seeding {repeats} datapoint done")
