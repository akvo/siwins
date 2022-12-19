import os
from sqlalchemy.orm import Session

TESTING = os.environ.get("TESTING")


def truncate(session: Session, table: str):
    session.execute(f"TRUNCATE TABLE {table} CASCADE;")
    session.execute(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1;")
    session.execute(f"UPDATE {table} SET id=nextval('{table}_id_seq');")
    session.commit()
    session.flush()
    return f"{table} Truncated"


def truncate_datapoint(session: Session):
    if not TESTING:
        # don't truncate when running test
        for table in ["data", "answer", "history"]:
            action = truncate(session=session, table=table)
            print(action)
