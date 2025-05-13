import os
import time
import flow.auth as flow_auth
from datetime import timedelta
from db.connection import Base, SessionLocal, engine
from db import crud_sync
from seeder.data_sync import data_sync
from seeder.delete_outlier_data import delete_outlier_schools
from utils.functions import refresh_materialized_data

from seeder.seeder_config import ENABLE_DELETE_OUTLIER_DATA


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()

start_time = time.process_time()

last_sync_url = crud_sync.get_last_sync(session=session)
sync_data = None
if last_sync_url:
    token = flow_auth.get_token()
    sync_data = flow_auth.get_data(url=last_sync_url.url, token=token)

if sync_data:
    errors = data_sync(
        token=token,
        session=session,
        sync_data=sync_data,
    )

    if ENABLE_DELETE_OUTLIER_DATA:
        # delete outlier
        delete_outlier_schools(session=session)

    # refresh materialized view
    refresh_materialized_data()


elapsed_time = time.process_time() - start_time
elapsed_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
print(f"\n-- SYNC DONE IN {elapsed_time}\n")
