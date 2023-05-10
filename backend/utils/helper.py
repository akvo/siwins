import re
import uuid
from datetime import datetime
from source.main_config import LOG_PATH


def get_uuid():
    return "-".join(str(uuid.uuid4()).split("-")[1:4])


def write_log(log_filename: str, log_content: str):
    today = datetime.today().strftime("%y%m%d")
    log_file = f"{log_filename}_{today}.txt"
    with open(f"{LOG_PATH}/{log_file}", mode="a+") as f:
        f.write(log_content + "\n")


def tr(obj):
    return " ".join(filter(lambda x: len(x), obj.strip().split(" ")))


def contain_numbers(inputString):
    return bool(re.search(r'\d', inputString))


class UUID(str):
    def __init__(self, string: str):
        self.uuid = get_uuid()
        self.str = f"{string}-{self.uuid}"


class HText(str):
    def __init__(self, string):
        self.obj = [string] if "|" not in string else string.split("|")
        self.clean = "|".join([tr(o) for o in self.obj])
        self.hasnum = contain_numbers(string)
