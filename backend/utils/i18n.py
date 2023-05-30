import enum


class EmailText(enum.Enum):
    incorrect_monitoring_round = {
        "title": "Incorrect Monitoring Round",
        "subject": "Incorrect Monitoring Round",
        "body": "",
        "message": '''
            <div style="color: #000;">
                Incorrect monitoring round value found.
                Please see the attachment.
            </div>
        ''',
    }
