import enum


class GeoLevels(enum.Enum):
    notset = [
        {"level": 0, "name": "provinsi", "alias": "Provinsi"},
        {"level": 1, "name": "kabkot", "alias": "Kabupaten / Kota"},
    ]
    solomon_island = [
        {"level": 0, "name": "NAME_1", "alias": "Province"},
    ]


# Landing Page
class GeoCenter(enum.Enum):
    notset = [106.3715, -8.84902]
    solomon_island = [-8.782, 160.957]
