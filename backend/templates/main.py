from typing import Optional
from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.connection import get_session
from utils.mailer import Email, MailTypeEnum

template_route = APIRouter()


@template_route.get(
    "/template/email",
    response_class=HTMLResponse,
    summary="get email template",
    name="template:email",
    tags=["Template"])
def get_email_template(
    req: Request,
    type: MailTypeEnum,
    send: Optional[bool] = False,
    session: Session = Depends(get_session)
):
    # need to add recipients
    email = Email(
        recipients=[{"Name": "galih", "Email": "galih@akvo.org"}],
        type=type
    )
    if send:
        email.send
    return email.data["Html-part"]
