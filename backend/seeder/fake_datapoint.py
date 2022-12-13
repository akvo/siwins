import os
import sys
import time
import json
import pandas as pd
from datetime import datetime
from faker import Faker
from db import crud_form
from db import crud_data
from db import crud_answer
from db import crud_question
from models.question import QuestionType
from models.answer import Answer
from db.connection import Base, SessionLocal, engine
from db.truncator import truncate
from source.geoconfig import GeoLevels

start_time = time.process_time()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()

config = GeoLevels.bali.value
levels = [c["name"] for c in config]

source_geo = f"./source/bali-topojson.json"
fake_geolocations_file = f"./source/fake-geolocations.csv"
fake_geolocations = os.path.exists(fake_geolocations_file)

sample_geo = False
if fake_geolocations:
    sample_geo = pd.read_csv(fake_geolocations_file)
    sample_geo = sample_geo.sample(frac=1)
    sample_geo = sample_geo.to_dict('records')
else:
    print(f"{fake_geolocations_file} is required")
    sys.exit()

with open(source_geo, 'r') as geo:
    geo = json.load(geo)
    ob = geo["objects"]
    ob_name = list(ob)[0]
parent_administration = set([
    d[levels[-2]]
    for d in [p["properties"] for p in ob[ob_name]["geometries"]]
])

forms = crud_form.get_form(session=session)
forms = [f.id for f in forms]

REGISTRATION_FORM_ID = 733030972
MONITORING_FORM_ID = 729240983

form_options = {
    "registration": REGISTRATION_FORM_ID,
    "monitoring": MONITORING_FORM_ID,
}

if len(sys.argv) < 2 or sys.argv[1] not in form_options.keys():
    print("you should provide one of these types: registration or monitoring")
    sys.exit()

if len(sys.argv) < 3:
    print("You should provide number of datapoints")
    sys.exit()

fake = Faker()
form_id = form_options.get(sys.argv[1])
form = crud_form.get_form_by_id(session=session, id=form_id)

repeats = int(sys.argv[2])
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
                # TODO: replace static_options with database

                if q.meta:
                    static_options = [
                        { "text": "Junior school", "value": "Junior school" },
                        { "text": "Primary school", "value": "Primary school" },
                        { "text": "High school", "value": "High school" }
                    ]
                    fa = fake.random_int(min=0, max=len(static_options) - 1)
                    answer.options = [static_options[fa].get('value')]
                    names.append(static_options[fa].get('value'))

            if q.type == QuestionType.number:
                fa = fake.random_int(min=10, max=50)
                answer.value = fa

            if q.type == QuestionType.date:
                fa = fake.date_this_century()
                fm = fake.random_int(min=11, max=12)
                fd = fa.strftime("%d")
                answer.text = f"2019-{fm}-{fd}"

            if q.type == QuestionType.geo and geo:
                answer.text = ("{}|{}").format(geo.get('lat'), geo.get('long'))

            if q.type == QuestionType.text:
                fa = fake.text(max_nb_chars=10)
                answer.text = fa
                if q.meta:
                    fa = geo.get('village')
                    answer.text = fa
                    names.append(fa)
            answers.append(answer)

    displayName = " - ".join(names)
    monitoring = form_id == MONITORING_FORM_ID
    geoVal = [geo.get('lat'), geo.get('long')]
    
    # add new datapoint
    data = crud_data.add_data(
        session=session,
        name=displayName,
        form=form_id,
        registration=False if monitoring else True,
        geo=geoVal,
        created=datetime.now(),
        answers=answers
    )
