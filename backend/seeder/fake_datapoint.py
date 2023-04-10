import os
import sys
import time
import json
import pandas as pd
import random
from datetime import datetime
from faker import Faker
from db import crud_form, crud_data, crud_option
from models.question import QuestionType
from models.answer import Answer
from db.connection import Base, SessionLocal, engine
from source.geoconfig import GeoLevels
from seeder.fake_history import generate_fake_history
from db.truncator import truncate_datapoint
from utils.functions import refresh_materialized_data

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
parent_administration = set(
    [
        d[levels[-2]]
        for d in [p["properties"] for p in ob[ob_name]["geometries"]]
    ]
)
forms = crud_form.get_form(session=session)
forms = [f.id for f in forms]

DEFAULT_NUMBER_OF_SEEDER = 10
repeats = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_NUMBER_OF_SEEDER

fake = Faker()
# truncate datapoints before running faker
truncate_datapoint(session=session)

for i in range(repeats):
    for form in forms:
        answers = []
        names = []
        iloc = i % (len(sample_geo) - 1)
        geo = sample_geo[iloc]

        # get form from database
        form = crud_form.get_form_by_id(session=session, id=form)

        monitoring = True if form.registration_form is not None else False

        datapoint = (
            crud_data.get_registration_only(session=session)
            if monitoring
            else None
        )
        for qg in form.question_group:
            for q in qg.question:
                answer = Answer(question=q.id, created=datetime.now())
                if q.type in [
                    QuestionType.option,
                    QuestionType.multiple_option,
                ]:
                    options = crud_option.get_option_by_question_id(
                        session=session, question=q.id
                    )
                    fa = random.choice(options)
                    answer.options = [fa.name]
                    if q.meta:
                        names.append(
                            datapoint.name
                            if monitoring and datapoint
                            else fa.name
                        )

                if q.type == QuestionType.number:
                    fa = fake.random_int(min=10, max=50)
                    answer.value = fa

                if q.type == QuestionType.date:
                    fa = fake.date_this_century()
                    fm = fake.random_int(min=11, max=12)
                    fd = fa.strftime("%d")
                    answer.text = f"2019-{fm}-{fd}"

                if q.type == QuestionType.geo and geo:
                    answer.text = ("{}|{}").format(geo["lat"], geo["long"])

                if q.type == QuestionType.text:
                    fa = fake.company()
                    answer.text = fa
                    if q.meta:
                        # fa += " - "
                        # fa += geo.get("village")
                        # answer.text = fa
                        names.append(fa)

                if q.type == QuestionType.cascade:
                    cascades = [geo.get(key) for key in [
                        "city", "district", "village"]]
                    answer.options = cascades
                    if q.meta:
                        names += cascades
                answers.append(answer)

        displayName = " - ".join(names)
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
        )

# populate data monitoring history

data_monitoring = crud_data.get_all_data(session=session, registration=False)
for dm in data_monitoring:
    generate_fake_history(session=session, datapoint=dm)
# refresh materialized view
refresh_materialized_data()
