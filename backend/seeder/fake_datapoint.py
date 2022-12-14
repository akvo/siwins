import os
import sys
import time
import json
import pandas as pd
import random
from uuid import uuid1
from datetime import datetime
from faker import Faker
from db import crud_form, crud_data, crud_option
from models.question import QuestionType
from models.answer import Answer
from db.connection import Base, SessionLocal, engine
from source.geoconfig import GeoLevels

start_time = time.process_time()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()

config = GeoLevels.bali.value
levels = [c["name"] for c in config]

source_geo = "./source/bali-topojson.json"
fake_geolocations_file = "./source/fake-geolocations.csv"
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
parent_administration = set([
    d[levels[-2]]
    for d in [p["properties"] for p in ob[ob_name]["geometries"]]
])
forms = crud_form.get_form(session=session)
forms = [f.id for f in forms]

MONITORING_FORM_ID = 729240983
if len(sys.argv) < 2:
    print("You should provide number of datapoints")
    sys.exit()

fake = Faker()

for form in forms:
    # get form from database
    form = crud_form.get_form_by_id(session=session, id=form)

    monitoring = form.id == MONITORING_FORM_ID

    datapoint_id = None
    if monitoring:
        datapoints = crud_data.get_all_data(session=session, registration=True)
        if len(datapoints):
            datapoint = random.choice(datapoints)
            datapoint_id = datapoint.id

    repeats = int(sys.argv[1])
    for i in range(repeats):
        answers = []
        names = []
        iloc = i % (len(sample_geo) - 1)
        geo = sample_geo[iloc]

        for qg in form.question_group:
            for q in qg.question:
                answer = Answer(question=q.id, created=datetime.now())
                if q.type in [
                    QuestionType.option, QuestionType.multiple_option
                ]:
                    if q.meta:
                        static_options = crud_option.get_option_by_question_id(
                            session=session, question=q.id
                        )
                        fa = random.choice(static_options)
                        answer.options = [fa.name]
                        names.append(fa.name)

                if q.type == QuestionType.number:
                    fa = fake.random_int(min=10, max=50)
                    answer.value = fa

                if q.type == QuestionType.date:
                    fa = fake.date_this_century()
                    fm = fake.random_int(min=11, max=12)
                    fd = fa.strftime("%d")
                    answer.text = f"2019-{fm}-{fd}"
                if q.type == QuestionType.geo and geo:
                    answer.text = ("{}|{}").format(geo['lat'], geo['long'])

                if q.type == QuestionType.text:
                    fa = fake.company()
                    answer.text = fa
                    if q.meta:
                        fa += " - "
                        fa += geo.get("village")
                        answer.text = fa
                        names.append(fa)
                answers.append(answer)

        displayName = " - ".join(names)
        geoVal = [geo.get("lat"), geo.get("long")]
        identifier = "-".join(str(uuid1()).split("-")[1:4])

        # add new datapoint
        print(datapoint_id)
        data = crud_data.add_data(
            datapoint_id=datapoint_id,
            identifier=identifier,
            session=session,
            name=displayName,
            form=form.id,
            registration=False if monitoring else True,
            geo=geoVal if not monitoring else None,
            created=datetime.now(),
            answers=answers,
        )
