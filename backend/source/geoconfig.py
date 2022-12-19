import enum


class GeoLevels(enum.Enum):
    notset = [
        {"level": 0, "name": "provinsi", "alias": "Provinsi"},
        {"level": 1, "name": "kabkot", "alias": "Kabupaten / Kota"},
    ]
    bali = [
        {"level": 0, "name": "NAME_2", "alias": "District"},
        {"level": 1, "name": "NAME_3", "alias": "Sub-District"},
        {"level": 2, "name": "NAME_4", "alias": "Village"},
    ]


# Landing Page
class GeoCenter(enum.Enum):
    notset = [106.3715, -8.84902]
    bali = [-8.670677602749869, 115.21310410475814]
