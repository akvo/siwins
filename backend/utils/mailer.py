import os
import enum
import smtplib
import pandas as pd
from bs4 import BeautifulSoup
from email.message import EmailMessage
from email.utils import formataddr
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader
from utils.i18n import EmailText
from typing_extensions import TypedDict
from datetime import datetime

from source.main import main_config

ERROR_PATH = main_config.ERROR_PATH


# =========================================================
# SMTP configuration
# =========================================================

# Every setting is read with `os.environ.get`, so the backend and the test
# suite boot without a relay configured. The Mailjet client this replaced read
# its credentials with `os.environ[...]` at import time, which took the whole
# application down whenever they were absent.
#
# The defaults describe the common case for a real relay: submission on port
# 587, upgraded in place with STARTTLS. Implicit SSL (conventionally port 465)
# is the other arrangement and has to be asked for. Neither mode is inferable
# from the port number, so a deployment that picks 465 must also set
# EMAIL_USE_SSL - with the wrong mode the client opens a plaintext socket
# against a TLS-only port and then blocks until the timeout.
#
# The fallbacks are written as `or` rather than as `get` defaults on purpose.
# Compose passes `- EMAIL_PORT=${EMAIL_PORT}` through as an empty string when
# the variable is unset in the shell, which is present as far as `get` is
# concerned: that would make `int("")` raise, and would read an empty
def get_smtp_config():
    """Resolve SMTP settings, inferring SSL/TLS defaults from port if unset."""
    host = os.environ.get("EMAIL_HOST")
    port = int(os.environ.get("EMAIL_PORT") or 587)
    user = os.environ.get("EMAIL_HOST_USER")
    password = os.environ.get("EMAIL_HOST_PASSWORD")

    use_ssl_env = os.environ.get("EMAIL_USE_SSL")
    if use_ssl_env is not None and use_ssl_env != "":
        use_ssl = use_ssl_env.lower() == "true"
    else:
        use_ssl = port == 465

    use_tls_env = os.environ.get("EMAIL_USE_TLS")
    if use_tls_env is not None and use_tls_env != "":
        use_tls = use_tls_env.lower() == "true"
    else:
        use_tls = port != 465

    from_addr = os.environ.get("EMAIL_FROM") or "noreply@akvo.org"
    return host, port, user, password, use_tls, use_ssl, from_addr


(
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_USE_TLS,
    EMAIL_USE_SSL,
    EMAIL_FROM,
) = get_smtp_config()

notification_recepients = os.environ.get("NOTIFICATION_RECIPIENTS", "")

loader = FileSystemLoader(".")
env = Environment(loader=loader)
html_template = env.get_template("./templates/main.html")


def html_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    body = soup.find("body")
    return "".join(body.get_text())


def format_recipients(recipients: List["Recipients"]) -> str:
    """Collapse recipient dicts into a single address header value.

    The `{"Email": ..., "Name": ...}` dict shape is inherited from Mailjet and
    kept as-is, because the call sites and the error report already build it;
    only the rendering into an RFC 5322 header changes here.
    """
    return ", ".join(
        formataddr((recipient.get("Name"), recipient["Email"].strip()))
        for recipient in recipients
    )


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
    def html(self) -> str:
        """Render the message body.

        Exposed separately from `data` because the `/template/email` route
        previews the rendered HTML without building or sending a message.
        """
        type = self.type.value
        return html_template.render(
            logo="",
            instance_name="instance",
            webdomain="",
            title=type["title"],
            body=self.body or type["body"],
            image="",
            message=type["message"],
            context=self.context,
        )

    @property
    def data(self) -> EmailMessage:
        if self.recipients:
            recipients = self.recipients
        else:
            raw_recipients = os.environ.get(
                "NOTIFICATION_RECIPIENTS", notification_recepients
            )
            recipients = [
                {"Email": email.strip()}
                for email in raw_recipients.split(",")
                if email.strip()
            ]
        html = self.html
        _, _, _, _, _, _, sender = get_smtp_config()

        message = EmailMessage()
        message["From"] = sender
        message["To"] = format_recipients(recipients)
        message["Subject"] = self.type.value["subject"]
        if self.bcc:
            message["Bcc"] = format_recipients(self.bcc)

        # Plain text is set first and HTML added as the alternative, which is
        # the order MIME asks for: least faithful representation first, so a
        # client that cannot render HTML still shows something readable.
        message.set_content(html_to_text(html))
        message.add_alternative(html, subtype="html")

        # The only attachment is the seed/sync error report. An unreadable
        # one means the CSV write itself failed, and losing the attachment
        # beats losing the notification that something went wrong at all.
        if self.attachment:
            try:
                with open(self.attachment, "rb") as handle:
                    content = handle.read()
            except (OSError, IOError) as e:
                print(e)
            else:
                message.add_attachment(
                    content,
                    maintype="text",
                    subtype="csv",
                    filename=self.attachment.split("/")[-1],
                )
        return message

    @property
    def send(self) -> bool:
        # The suite exercises message construction but must never reach a
        # relay. `TESTING` is already set by the pytest fixtures.
        if os.environ.get("TESTING"):
            return True
        (
            host,
            port,
            user,
            password,
            use_tls,
            use_ssl,
            _,
        ) = get_smtp_config()
        # smtplib silently skips connecting when handed a falsy host and then
        # fails several calls later with "please run connect() first", which
        # says nothing about the actual problem. Name it here instead.
        if not host:
            raise RuntimeError("EMAIL_HOST is not configured")
        smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        # Mailjet bounded its connection at nothing at all, so any finite
        # timeout is the improvement; nothing here is worth tuning.
        with smtp_class(host, port, timeout=30) as smtp:
            # STARTTLS upgrades a plaintext connection, so it is meaningless
            # once implicit SSL has already wrapped the socket.
            if use_tls and not use_ssl:
                smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.send_message(self.data)
        return True
