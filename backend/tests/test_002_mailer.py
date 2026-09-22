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
        email = Email(
            type=MailTypeEnum.error, attachment=str(error_file)
        )
        message = email.data
        attachments = list(message.iter_attachments())
        assert len(attachments) == 1
        assert attachments[0].get_filename() == "error-seed-260101.csv"
        assert attachments[0].get_content_type() == "text/csv"
