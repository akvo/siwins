from sqlalchemy.orm import Session
from models.cascade import Cascade, CascadeDict
# from typing import List, Optional
# from sqlalchemy import and_


def add_cascade(session: Session, data: Cascade) -> CascadeDict:
    session.add(data)
    session.commit()
    session.flush()
    session.refresh(data)
    return data
