import os
import enum
import shutil
from pathlib import Path
from google.cloud import storage

from source.main import main_config

DOWNLOAD_PATH = main_config.DOWNLOAD_PATH
FAKE_STORAGE_PATH = main_config.FAKE_STORAGE_PATH


bucket_name = "siwins"


class StorageFolder(enum.Enum):
    download = "download"
    test = "test"
    error = "error"


def upload(file: str, folder: str, filename: str = None, public: bool = False):
    if not filename:
        filename = file.split("/")[-1]
    TESTING = os.environ.get("TESTING")
    STORAGE_LOCATION = os.environ.get("STORAGE_LOCATION")
    if TESTING:
        fake_location = f"{FAKE_STORAGE_PATH}/{filename}"
        shutil.copy2(file, fake_location)
        return fake_location
    if STORAGE_LOCATION:
        location = f"{STORAGE_LOCATION}/{filename}"
        shutil.copy2(file, location)
        return location
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    destination_blob_name = f"{folder}/{filename}"
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file)
    os.remove(file)
    if public:
        blob.make_public()
        return blob.public_url
    return blob.name


def delete(url: str):
    file = url.split("/")[-1]
    folder = url.split("/")[-2]
    TESTING = os.environ.get("TESTING")
    STORAGE_LOCATION = os.environ.get("STORAGE_LOCATION")
    if TESTING or STORAGE_LOCATION:
        os.remove(url)
        return url
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"{folder}/{file}")
    blob.delete()
    return blob.name


def check(url: str):
    TESTING = os.environ.get("TESTING")
    STORAGE_LOCATION = os.environ.get("STORAGE_LOCATION")
    if TESTING or STORAGE_LOCATION:
        path = Path(url)
        return path.is_file()
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    return storage.Blob(bucket=bucket, name=url).exists(storage_client)


def download(url):
    TESTING = os.environ.get("TESTING")
    STORAGE_LOCATION = os.environ.get("STORAGE_LOCATION")
    if TESTING or STORAGE_LOCATION:
        tmp_file = url.split("/")[-1]
        return f"{FAKE_STORAGE_PATH}/{tmp_file}"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(url)
    tmp_file = url.split("/")[-1]
    tmp_file = f"{DOWNLOAD_PATH}/{tmp_file}"
    blob.download_to_filename(tmp_file)
    return tmp_file
