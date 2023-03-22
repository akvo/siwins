import os
import json
import flow.auth as flow_auth
from seeder.form import form_seeder
from seeder.datapoint import datapoint_seeder
from db.connection import Base, SessionLocal, engine
from db import crud_sync
from db.truncator import truncate, truncate_datapoint
from utils.functions import refresh_materialized_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTING = os.environ.get("TESTING")
Base.metadata.create_all(bind=engine)
session = SessionLocal()


forms = []
forms_config = "./source/forms.json"
with open(forms_config) as json_file:
    forms = json.load(json_file)

if not TESTING:
    # don't truncate when running test
    for table in ["sync", "form", "question_group", "question", "option"]:
        action = truncate(session=session, table=table)
        print(action)

    truncate_datapoint(session=session)

token = flow_auth.get_token()

# init sync
sync_res = flow_auth.init_sync(token=token)
if sync_res.get("nextSyncUrl"):
    sync_res = crud_sync.add_sync(
        session=session, url=sync_res.get("nextSyncUrl")
    )
    print("------------------------------------------")
    print(f"Init Sync URL: {sync_res.url}")
    print("------------------------------------------")

form_seeder(session=session, token=token, forms=forms)
datapoint_seeder(session=session, token=token, forms=forms)
# refresh materialized view
refresh_materialized_data()
