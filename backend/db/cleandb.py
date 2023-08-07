from db.truncator import truncate
from db.connection import SessionLocal

session = SessionLocal()

tables = [
    "history",
    "answer",
    "data",
    "option",
    "question",
    "question_group",
    "form",
    "administration",
    "sync",
    "jobs",
]


for t in tables:
    print(f"{t} CLEANED")
    action = truncate(session=session, table=t)
exit(0)
