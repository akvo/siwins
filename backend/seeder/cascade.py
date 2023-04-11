import os
import json
import requests
from time import sleep
import flow.auth as flow_auth
from typing import List, Optional
from db.connection import Base, SessionLocal, engine
from db.truncator import truncate
from db import crud_cascade
from models.cascade import Cascade

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
    action = truncate(session=session, table="cascade")
    print(action)


def seed_cascade(source: str, ids: List[int], level: Optional[int] = 0):
    if not ids:
        return None
    for id in ids:
        try:
            res = flow_auth.get_cascade(source=source, id=id)
        except requests.exceptions.RequestException:
            print("Sleep 2 second...")
            sleep(2)
            print("Continue...")
            res = flow_auth.get_cascade(source=source, id=id)
            # seed_cascade(source=source, ids=ids, level=level)
        cids = []
        if res:
            for r in res:
                cascade = Cascade(
                    id=r.get('id'),
                    parent=r.get('parent') or None,
                    name=r.get('name'),
                    level=level)
                saved = crud_cascade.add_cascade(
                    session=session, data=cascade)
                cids.append(saved.id)
        if not cids:
            return None
        seed_cascade(source=source, ids=cids, level=level + 1)


for form in forms:
    if not form.get("cascade_resources"):
        continue
    for cr in form.get("cascade_resources"):
        print("Seeding...")
        seed_cascade(source=cr, ids=[0])
        print(f"Seeding cascade {cr} done")
