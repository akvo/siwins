import os
import json
from seeder.form import form_seeder
from db.connection import Base, SessionLocal, engine
from db.truncator import truncate, truncate_datapoint

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

form_seeder(session=session, forms=forms)
