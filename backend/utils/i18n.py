import enum


class EmailText(enum.Enum):
    error = {
        "title": "Seed/Sync Error",
        "subject": "Seed/Sync Error Found",
        "body": "",
        "message": '''
            <div style="color: #000;">
                Error found while seed/sync data from Flow API.
                Please take a look into the attachment for the details.
            </div>
        ''',
    }
