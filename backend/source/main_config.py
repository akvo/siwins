# general config for project

import enum

FLOW_INSTANCE = "sig"
CLASS_PATH = "solomon_island"

SOURCE_PATH = "./source"
TOPO_JSON_PATH = f"{SOURCE_PATH}/solomon-island-topojson.json"
FRONTEND_CONFIG_PATH = f"{SOURCE_PATH}/config"

FORM_PATH = f"{SOURCE_PATH}/forms"
FORM_CONFIG_PATH = f"{FORM_PATH}/forms.json"
DATAPOINT_PATH = f"{SOURCE_PATH}/datapoints"
CASCADE_PATH = f"{SOURCE_PATH}/cascades"
ADMINISTRATION_PATH = f"{SOURCE_PATH}/administration"

# to identify if monitoring form available on questionnaire
# if we add monitoting form on forms.json, we need to change
# MONITORING_FORM value to True
MONITORING_FORM = False


class QuestionConfig(enum.Enum):
    year_conducted = 654960929
    school_information = 638730933


class SchoolInformationEnum(enum.Enum):
    province = "province"
    school_type = "school_type"
    school_name = "school_name"
    school_code = "school_code"


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
