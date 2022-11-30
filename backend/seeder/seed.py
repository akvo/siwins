import os
import json
import flow.auth as flow_auth
from seeder.form import form_seeder
from seeder.datapoint import datapoint_seeder
from db.connection import Base, SessionLocal, engine
from db import crud_sync
from db.truncator import truncate


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()


forms = []
forms_config = "./config/forms.json"
with open(forms_config) as json_file:
    forms = json.load(json_file)

for table in ["sync"]:
    action = truncate(session=session, table=table)
    print(action)

token = flow_auth.get_token()

# init sync
sync_res = flow_auth.init_sync(token=token)
if sync_res.get('nextSyncUrl'):
    sync_res = crud_sync.add_sync(
        session=session, url=sync_res.get('nextSyncUrl'))
    print("------------------------------------------")
    print(f"Init Sync URL: {sync_res.url}")
    print("------------------------------------------")

form_seeder(token=token, forms=forms)
datapoint_seeder(token=token, forms=forms)
