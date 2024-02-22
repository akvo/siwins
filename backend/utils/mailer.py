import os
import enum
import base64
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Optional
from mailjet_rest import Client
from jinja2 import Environment, FileSystemLoader
from utils.i18n import EmailText
from typing_extensions import TypedDict
from datetime import datetime

from source.main import main_config

ERROR_PATH = main_config.ERROR_PATH


mjkey = os.environ["MAILJET_APIKEY"]
mjsecret = os.environ["MAILJET_SECRET"]
notification_recepients = os.environ["NOTIFICATION_RECIPIENTS"]

mailjet = Client(auth=(mjkey, mjsecret))
loader = FileSystemLoader(".")
env = Environment(loader=loader)
html_template = env.get_template("./templates/main.html")
ftype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ftype += ";base64"


def send(data):
    res = mailjet.send.create(data=data)
    res = res.json()
    return res


def html_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    body = soup.find("body")
    return "".join(body.get_text())


def format_attachment(file):
    try:
        open(file, "r")
    except (OSError, IOError) as e:
        print(e)
        return None
    return {
        "ContentType": ftype,
        "Filename": file.split("/")[-1],
        "content": base64.b64encode(open(file, "rb").read()).decode("UTF-8"),
    }


def send_error_email(error: List, filename: Optional[str] = None):
    today = datetime.today().strftime("%y%m%d")
    error_list = pd.DataFrame(error)
    error_list = error_list[
        list(filter(lambda x: x != "error", list(error_list)))
    ]
    fname = "error" if not filename else filename
    error_file = f"{ERROR_PATH}/{fname}-{today}.csv"
    error_list = error_list.to_csv(error_file, index=False)
    # error email
    email = Email(type=MailTypeEnum.error, attachment=error_file)
    email.send
    # end of email


class Recipients(TypedDict):
    Email: str
    Name: str


class MailTypeEnum(enum.Enum):
    error = "error"


class Email:
    def __init__(
        self,
        type: MailTypeEnum,
        recipients: Optional[List[Recipients]] = None,
        bcc: Optional[List[Recipients]] = None,
        attachment: Optional[str] = None,
        context: Optional[str] = None,
        body: Optional[str] = None,
    ):
        self.type = EmailText[type.value]
        self.recipients = recipients
        self.bcc = bcc
        self.attachment = attachment
        self.context = context
        self.body = body

    @property
    def data(self):
        recipients = notification_recepients.split(",")
        recipients = [{"Email": email} for email in recipients]
        type = self.type.value
        body = type["body"]
        if self.body:
            body = self.body
        if self.recipients:
            recipients = self.recipients
        html = html_template.render(
            logo="",
            instance_name="instance",
            webdomain="",
            title=type["title"],
            body=body,
            image="",
            message=type["message"],
            context=self.context,
        )
        payload = {
            "FromEmail": "noreply@akvo.org",
            "Subject": type["subject"],
            "Html-part": html,
            "Text-part": html_to_text(html),
            "Recipients": recipients,
        }
        if self.bcc:
            payload.update({"Bcc": self.bcc})
        if self.attachment:
            attachment = format_attachment(self.attachment)
            payload.update({"Attachments": [attachment]})
        return payload

    @property
    def send(self) -> int:
        TESTING = os.environ.get("TESTING")
        if TESTING:
            return True
        res = mailjet.send.create(data=self.data)
        return res.status_code == 200
