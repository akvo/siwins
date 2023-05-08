import uuid


def get_uuid():
    return "-".join(str(uuid.uuid4()).split("-")[1:4])


class UUID(str):
    def __init__(self, string: str):
        self.uuid = get_uuid()
        self.str = f"{string}-{self.uuid}"
