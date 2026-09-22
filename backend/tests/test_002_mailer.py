import sys
import pytest
from sqlalchemy.orm import Session
from utils.mailer import Email, MailTypeEnum

pytestmark = pytest.mark.asyncio
sys.path.append("..")


class TestMailer:
    @pytest.mark.asyncio
    async def test_email_data(self, session: Session) -> None:
        recipients = [{"Email": "support@akvo.org", "Name": "Akvo Support"}]
        email = Email(recipients=recipients, type=MailTypeEnum.error)
        message = email.data
        assert message["To"] == "Akvo Support <support@akvo.org>"
        assert message["From"] == "noreply@akvo.org"
        assert message["Subject"] == "Seed/Sync Error Found"
        # A plain-text body with an HTML alternative: clients that cannot
        # render HTML still receive the notification.
        assert message.get_content_type() == "multipart/alternative"
        assert message.get_body(("html",)) is not None
        assert message.get_body(("plain",)) is not None

    @pytest.mark.asyncio
    async def test_email_with_attachment(
        self, session: Session, tmp_path
    ) -> None:
        # The seed/sync error report is the reason the attachment path exists,
        # so it is exercised here rather than left to the caller.
        error_file = tmp_path / "error-seed-260101.csv"
        error_file.write_text("school,error\n1,missing\n")
        email = Email(type=MailTypeEnum.error, attachment=str(error_file))
        message = email.data
        attachments = list(message.iter_attachments())
        assert len(attachments) == 1
        assert attachments[0].get_filename() == "error-seed-260101.csv"
        assert attachments[0].get_content_type() == "text/csv"

    @pytest.mark.asyncio
    async def test_email_default_notification_recipients(
        self, session: Session, monkeypatch
    ) -> None:
        monkeypatch.setenv(
            "NOTIFICATION_RECIPIENTS", "dev1@akvo.org, dev2@akvo.org, "
        )
        email = Email(type=MailTypeEnum.error)
        message = email.data
        assert message["To"] == "dev1@akvo.org, dev2@akvo.org"

    @pytest.mark.asyncio
    async def test_email_empty_notification_recipients(
        self, session: Session, monkeypatch
    ) -> None:
        monkeypatch.setenv("NOTIFICATION_RECIPIENTS", "")
        email = Email(type=MailTypeEnum.error)
        message = email.data
        assert message["To"] == ""

    def test_smtp_config_port_465_ssl_auto_detection(
        self, monkeypatch
    ) -> None:
        from utils.mailer import get_smtp_config

        monkeypatch.setenv("EMAIL_PORT", "465")
        monkeypatch.delenv("EMAIL_USE_SSL", raising=False)
        monkeypatch.delenv("EMAIL_USE_TLS", raising=False)
        _, port, _, _, use_tls, use_ssl, _ = get_smtp_config()
        assert port == 465
        assert use_ssl is True
        assert use_tls is False

    def test_smtp_config_port_587_starttls_auto_detection(
        self, monkeypatch
    ) -> None:
        from utils.mailer import get_smtp_config

        monkeypatch.setenv("EMAIL_PORT", "587")
        monkeypatch.delenv("EMAIL_USE_SSL", raising=False)
        monkeypatch.delenv("EMAIL_USE_TLS", raising=False)
        _, port, _, _, use_tls, use_ssl, _ = get_smtp_config()
        assert port == 587
        assert use_ssl is False
        assert use_tls is True

    def test_smtp_config_explicit_override(self, monkeypatch) -> None:
        from utils.mailer import get_smtp_config

        monkeypatch.setenv("EMAIL_PORT", "465")
        monkeypatch.setenv("EMAIL_USE_SSL", "false")
        monkeypatch.setenv("EMAIL_USE_TLS", "true")
        _, port, _, _, use_tls, use_ssl, _ = get_smtp_config()
        assert port == 465
        assert use_ssl is False
        assert use_tls is True
