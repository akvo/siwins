import enum


class ValidationText(enum.Enum):
    header_name_missing = "Header name is missing"


class EmailText(enum.Enum):
    test = {
        "title": "Data Validation Success",
        "subject": "Data Validation",
        "body": "filename",
        "message": '''
                  <div style="color: #11A840;">
                      Data Validation have passed successfully!
                  </div>
                  ''',
    }
