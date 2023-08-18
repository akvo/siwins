import subprocess
from sqlalchemy import text
from db.connection import engine
from typing import List, Optional

from source.main import main_config, INSTANCE_NAME

SchoolInformationEnum = main_config.SchoolInformationEnum
CascadeLevels = main_config.CascadeLevels


school_information_cascade = CascadeLevels.school_information.value


def refresh_materialized_view_query():
    return text("""
        REFRESH MATERIALIZED VIEW advance_filter;
        REFRESH MATERIALIZED VIEW province_option_answer;
        REFRESH MATERIALIZED VIEW province_number_answer;
        REFRESH MATERIALIZED VIEW data_answer;
    """)


def refresh_materialized_data():
    categories = f"./source/{INSTANCE_NAME}/category.json"
    command = f"akvo-responsegrouper --config {categories}"
    subprocess.check_output(command, shell=True, text=True)

    query = refresh_materialized_view_query()
    engine.execute(query)


def extract_school_information(
    school_information: List[str],
    to_object: Optional[bool] = False
):
    province_lv = school_information_cascade.get(
        SchoolInformationEnum.province.value)
    school_type_lv = school_information_cascade.get(
        SchoolInformationEnum.school_type.value)
    school_name_lv = school_information_cascade.get(
        SchoolInformationEnum.school_name.value)
    school_code_lv = school_information_cascade.get(
        SchoolInformationEnum.school_code.value)
    # province, school name - code
    current_province = school_information[province_lv]
    current_school_type = school_information[school_type_lv]
    current_school_name = school_information[school_name_lv]
    current_school_code = school_information[school_code_lv]
    if (to_object):
        return {
            SchoolInformationEnum.province.value: current_province,
            SchoolInformationEnum.school_type.value: current_school_type,
            SchoolInformationEnum.school_name.value: current_school_name,
            SchoolInformationEnum.school_code.value: current_school_code
        }
    return (
        current_province, current_school_type,
        current_school_name, current_school_code
    )
