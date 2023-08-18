import os
import json
from db.connection import Base, SessionLocal, engine
from db.truncator import truncate
from seeder.cascade_util import seed_cascade

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
    action = truncate(session=session, table="cascade")
    print(action)


seed_cascade(session=session, forms=forms)
