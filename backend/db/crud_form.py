from typing import List, Optional
# from db.connection import engine
from sqlalchemy.orm import Session
from models.form import Form, FormDict, FormBase


def add_form(
    session: Session,
    name: str,
    id: Optional[int] = None,
    version: Optional[float] = None,
    description: Optional[str] = None,
    registration_form: Optional[int] = None,
) -> FormDict:
    form = Form(
        id=id,
        name=name,
        version=version if version else 1.0,
        description=description,
        registration_form=registration_form,
    )
    session.add(form)
    session.commit()
    session.flush()
    session.refresh(form)
    return form


def get_form(session: Session) -> List[FormDict]:
    return session.query(Form).all()


def get_form_by_id(session: Session, id: int) -> FormBase:
    return session.query(Form).filter(Form.id == id).first()


def get_form_name(session: Session) -> str:
    form = session.query(Form.name).first()
    return form.name


# def update_form(
#     session: Session,
#     id: int,
#     name: str,
#     version: Optional[float] = None,
#     description: Optional[str] = None,
#     registration_form: Optional[int] = None,
# ) -> FormDict:
#     form = session.query(Form).filter(Form.id == id).first()
#     form.name = name
#     if not form.version:
#         form.version = 1.0
#     if form.version:
#         form.version = form.version + 1
#     if version:
#         form.version = version
#     form.description = description
#     form.registration_form = registration_form
#     session.commit()
#     session.flush()
#     session.refresh(form)
#     return form


# def delete_by_id(session: Session, id: int) -> None:
#     session.query(Form).filter(Form.id == id).delete()
#     session.commit()


# UTIL, with private session not from route session
# def get_form_list():
#     session = Session(engine)
#     form = session.query(Form).all()
#     return [f"{f.id} - {f.name}" for f in form]


# def get_registration_form(session: Session) -> FormDict:
#     return session.query(Form).filter(Form.registration_form.is_(None))


def get_monitoring_form(session: Session) -> FormDict:
    return (
        session.query(Form).filter(Form.registration_form.is_not(None)).all()
    )
