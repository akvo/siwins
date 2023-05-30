import os
from bs4 import BeautifulSoup
import enum
from typing import List, Optional
from mailjet_rest import Client
from jinja2 import Environment, FileSystemLoader
import base64
from utils.i18n import EmailText
from typing_extensions import TypedDict

mjkey = os.environ['MAILJET_APIKEY']
mjsecret = os.environ['MAILJET_SECRET']

mailjet = Client(auth=(mjkey, mjsecret))
loader = FileSystemLoader('.')
env = Environment(loader=loader)
html_template = env.get_template("./templates/main.html")
ftype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
ftype += ';base64'


def send(data):
    res = mailjet.send.create(data=data)
    res = res.json()
    return res


def html_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    body = soup.find('body')
    return "".join(body.get_text())


def format_attachment(file):
    try:
        open(file, "r")
    except (OSError, IOError) as e:
        print(e)
        return None
    return {
        "ContentType": ftype,
        "Filename": file.split("/")[2],
        "content": base64.b64encode(open(file, "rb").read()).decode('UTF-8')
    }


class Recipients(TypedDict):
    Email: str
    Name: str


class MailTypeEnum(enum.Enum):
    incorrect_monitoring_round = "incorrect_monitoring_round"


class Email:
    def __init__(
        self,
        recipients: List[Recipients],
        type: MailTypeEnum,
        bcc: Optional[List[Recipients]] = None,
        attachment: Optional[str] = None,
        context: Optional[str] = None,
        body: Optional[str] = None
    ):
        self.type = EmailText[type.value]
        self.recipients = recipients
        self.bcc = bcc
        self.attachment = attachment
        self.context = context
        self.body = body

    @property
    def data(self):
        type = self.type.value
        body = type["body"]
        if self.body:
            body = self.body
        html = html_template.render(
            logo="",
            instance_name="instance",
            webdomain="",
            title=type["title"],
            body=body,
            image="",
            message=type["message"],
            context=self.context
        )
        payload = {
            "FromEmail": "noreply@akvo.org",
            "Subject": type["subject"],
            "Html-part": html,
            "Text-part": html_to_text(html),
            "Recipients": self.recipients,
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
