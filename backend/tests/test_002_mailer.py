import sys
import pytest
from sqlalchemy.orm import Session
from utils.mailer import Email, MailTypeEnum

pytestmark = pytest.mark.asyncio
sys.path.append("..")


class TestMailer():
    @pytest.mark.asyncio
    async def test_email_data(self, session: Session) -> None:
        recipients = [{
            "Email": "support@akvo.org",
            "Name": "Akvo Support"
        }]
        email = Email(
            recipients=recipients,
            type=MailTypeEnum.error
        )
        data = email.data
        assert data["Recipients"] == recipients
        assert data["FromEmail"] == "noreply@akvo.org"
        assert data["Subject"] == "Seed/Sync Error Found"
        # assert email.send is True
