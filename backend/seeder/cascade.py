import os
import json
from db.connection import Base, SessionLocal, engine
from db.truncator import truncate
from source.main_config import FORM_CONFIG_PATH
from seeder.cascade_util import seed_cascade

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTING = os.environ.get("TESTING")
Base.metadata.create_all(bind=engine)
session = SessionLocal()


forms = []
with open(FORM_CONFIG_PATH) as json_file:
    forms = json.load(json_file)

if not TESTING:
    # don't truncate when running test
    action = truncate(session=session, table="cascade")
    print(action)


seed_cascade(session=session, forms=forms)
