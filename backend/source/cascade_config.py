import enum


class CascadeTypes(enum.Enum):
    school_information = 'qid'


class CascadeLevels(enum.Enum):
    school_information = {
        "province": 0,
        "school_type": 1,
        "school_name": 2,
        "school_code": 3
    }
