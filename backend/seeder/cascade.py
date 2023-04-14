import os
import json
import requests
import pandas as pd
from time import sleep
import flow.auth as flow_auth
from sqlalchemy.orm import Session
from typing import List, Optional
from db.connection import Base, SessionLocal, engine
from db.truncator import truncate
from db import crud_cascade
from models.cascade import Cascade
from source.main_config import FORM_CONFIG_PATH, CASCADE_PATH, \
    TESTING_CASCADE_FILE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTING = os.environ.get("TESTING")
Base.metadata.create_all(bind=engine)
session = SessionLocal()


def save_cascade(
    session: Session,
    source: str, question: int,
    ids: List[int], level: Optional[int] = 0
):
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
        cids = []
        if res:
            for r in res:
                cascade = Cascade(
                    id=r.get('id'),
                    parent=r.get('parent') or None,
                    name=r.get('name'),
                    level=level,
                    question=question)
                saved = crud_cascade.add_cascade(
                    session=session, data=cascade)
                cids.append(saved.id)
        if not cids:
            return None
        save_cascade(
            source=source, question=question, ids=cids, level=level + 1)


def seed_cascade(session: Session, forms: List[dict]):
    for form in forms:
        if not form.get("cascade_resources"):
            continue
        for cr in form.get("cascade_resources"):
            print("Seeding...")
            sqlite_filename = cr.get("source") if not TESTING \
                else TESTING_CASCADE_FILE
            qid = cr.get("question")
            filepath = f"{CASCADE_PATH}/{sqlite_filename}.csv"
            cascade_file = os.path.exists(filepath)
            if cascade_file:
                print("Seeding from file...")
                df = pd.read_csv(filepath)
                df = df.fillna(0)
                for index, row in df.iterrows():
                    cascade = Cascade(
                        id=row["id"],
                        parent=row["parent"] if row["parent"] else None,
                        name=row["name"],
                        level=row["level"],
                        question=qid)
                    crud_cascade.add_cascade(
                        session=session, data=cascade)
            if not cascade_file and not TESTING:
                print("Seeding from source...")
                save_cascade(
                    session=session, source=sqlite_filename,
                    question=qid, ids=[0])
                # get all cascade & save to csv
                cascades = crud_cascade.get_all_cascade(session=session)
                cascades = [c.serialize for c in cascades]
                df = pd.DataFrame(cascades)
                df = df.drop(columns=["children"])
                df.to_csv(filepath, index=False)
            print(f"Seeding cascade {sqlite_filename} done")


forms = []
with open(FORM_CONFIG_PATH) as json_file:
    forms = json.load(json_file)

if not TESTING:
    # don't truncate when running test
    action = truncate(session=session, table="cascade")
    print(action)


seed_cascade(session=session, forms=forms)
