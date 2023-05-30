import enum


class ValidationText(enum.Enum):
    incorrect_monitoring_round = "incorrect monitoring round"
    school_monitoring_exist = "school in same monitoring round already exist"


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
