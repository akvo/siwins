import os
import json
import flow.auth as flow_auth
from seeder.form import form_seeder
from seeder.datapoint import datapoint_seeder
from db.connection import Base, SessionLocal, engine
from db import crud_sync
from db.truncator import truncate, truncate_datapoint
from utils.functions import refresh_materialized_data

from source.main import main_config

FORM_CONFIG_PATH = main_config.FORM_CONFIG_PATH


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTING = os.environ.get("TESTING")
Base.metadata.create_all(bind=engine)
session = SessionLocal()


forms = []
with open(FORM_CONFIG_PATH) as json_file:
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

form_seeder(session=session, forms=forms)
datapoint_seeder(session=session, token=token, forms=forms)
# refresh materialized view
refresh_materialized_data()
