import os
import time
import flow.auth as flow_auth
from datetime import timedelta
from db.connection import Base, SessionLocal, engine
from db import crud_sync
from db import crud_data
from models.data import Data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
session = SessionLocal()

start_time = time.process_time()


def sync(sync_data: dict):
    changes = sync_data.get('changes')
    print(changes)
    next_sync_url = sync_data.get('nextSyncUrl')
    # manage form instance changes
    for data in changes.get('formInstanceChanged'):
        current_data = crud_data.get_data_by_id(
            session=session, id=data.get('dataPointId'))
        if not current_data:
            # add new
            continue
        # update
        updated_data = Data(
            name=data.get('displayName'),
            form=data.get('formId'),
            geo=current_data.geo,
            updated=data.get('modifiedAt'),
            created=current_data.created)
        crud_data.update_data(session=session, data=updated_data)
    # call next sync URL
    sync_data = flow_auth.get_data(url=next_sync_url, token=token)
    if sync_data:
        sync(sync_data=sync_data)


last_sync_url = crud_sync.get_last_sync(session=session)
sync_data = None
if last_sync_url:
    token = flow_auth.get_token()
    sync_data = flow_auth.get_data(
        url=last_sync_url.url, token=token)

if sync_data:
    sync(sync_data=sync_data)


elapsed_time = time.process_time() - start_time
elapsed_time = str(timedelta(seconds=elapsed_time)).split(".")[0]
print(f"\n-- SYNC DONE IN {elapsed_time}\n")
