import pytest
import os
from sqlalchemy.orm import Session
from utils.storage import upload, delete, check, StorageFolder

from source.main import main_config

TEST_PATH = main_config.TEST_PATH
DOWNLOAD_PATH = main_config.DOWNLOAD_PATH
FAKE_STORAGE_PATH = main_config.FAKE_STORAGE_PATH
LOG_PATH = main_config.LOG_PATH


def create_test_file():
    # create a random file
    test_file = f"{TEST_PATH}/test_file.txt"
    with open(test_file, mode="a+") as f:
        f.write("Lorem ipsum dolor sit amet.")
    return test_file


class TestStorage:
    @pytest.mark.asyncio
    async def test_dir_exist(self, session: Session) -> None:
        dirs = [TEST_PATH, DOWNLOAD_PATH, FAKE_STORAGE_PATH, LOG_PATH]
        for dr in dirs:
            if not os.path.exists(dr):
                os.makedirs(dr)
        # check exist
        for dr in dirs:
            assert os.path.exists(dr) is True

    @pytest.mark.asyncio
    async def test_upload_file_to_bucket(self, session: Session) -> None:
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            test_file = create_test_file()
            uploaded_file = upload(test_file, StorageFolder.test.value)
            assert check(uploaded_file) is True
        else:
            print("SKIPPING STORAGE UPLOAD TEST")
            assert True is True

    @pytest.mark.asyncio
    async def test_delete_file_from_bucket(self, session: Session) -> None:
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            # use administration CSV
            test_file = create_test_file()
            uploaded_file = upload(test_file, StorageFolder.test.value)
            delete(url=uploaded_file)
            assert check(uploaded_file) is False
        else:
            print("SKIPPING STORAGE DELETE TEST")
            assert True is True
