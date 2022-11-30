from sqlalchemy.orm import Session
from models.sync import Sync, SyncDict
from sqlalchemy import desc


def add_sync(session: Session, url: str) -> SyncDict:
    sync = Sync(url=url)
    session.add(sync)
    session.commit()
    session.flush()
    session.refresh(sync)
    return sync


def get_last_sync(session: Session) -> SyncDict:
    return session.query(Sync).order_by(
        desc(Sync.id)).first()
