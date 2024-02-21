# general config for project

import enum

FLOW_INSTANCE = "sig"
CLASS_PATH = "solomon_island"

SOURCE_PATH = "./source/production"
TOPO_JSON_PATH = f"{SOURCE_PATH}/solomon-island-topojson.json"
FRONTEND_CONFIG_PATH = f"{SOURCE_PATH}/config"

FORM_PATH = f"{SOURCE_PATH}/forms"
FORM_CONFIG_PATH = f"{FORM_PATH}/forms.json"
DATAPOINT_PATH = f"{SOURCE_PATH}/datapoints"
CASCADE_PATH = f"{SOURCE_PATH}/cascades"
ADMINISTRATION_PATH = f"{SOURCE_PATH}/administration"

# only for testing
TESTING_CASCADE_FILE = "cascade-654850917-v1.sqlite"

# to identify if monitoring form available on questionnaire
# if we add monitoting form on forms.json, we need to change
# MONITORING_FORM value to True
MONITORING_FORM = False

# to handle incorrect monitoring round data
MONITORING_ROUND = 2023

TMP_PATH = "./tmp"
FAKE_STORAGE_PATH = f"{TMP_PATH}/fake-storage"
LOG_PATH = f"{TMP_PATH}/log"
DOWNLOAD_PATH = f"{TMP_PATH}/download"
TEST_PATH = f"{TMP_PATH}/test"
ERROR_PATH = f"{TMP_PATH}/error"


class QuestionConfig(enum.Enum):
    year_conducted = 596240919
    school_information = 634200919


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
        "school_code": 3,
    }


class CascadeNames(enum.Enum):
    school_information = {
        "province": "Province",
        "school_type": "School Type",
        "school_name": "School Name",
        "school_code": "School Code",
    }


class ResponseGrouperCustomConfig(enum.Enum):
    water = {"question_group": None, "category_type": "jmp"}
    sanitation = {"question_group": None, "category_type": "jmp"}
    hygiene = {"question_group": None, "category_type": "jmp"}
    toilet_category = {"question_group": 7, "category_type": None}

    @classmethod
    def to_dict(cls):
        return [{**member.value, "name": member.name} for member in cls]
