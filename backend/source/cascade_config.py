import enum


class CascadeTypes(enum.Enum):
    school_information = 638730933


class CascadeLevels(enum.Enum):
    school_information = {
        "province": 0,
        "school_type": 1,
        "school_name": 2,
        "school_code": 3
    }


class CascadeNames(enum.Enum):
    school_information = {
        "province": "Province",
        "school_type": "School Type",
        "school_name": "School Name",
        "school_code": "School Code"
    }
