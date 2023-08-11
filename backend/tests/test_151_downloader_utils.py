import os
import sys
import pandas as pd
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from utils.downloader import generate_download_data
from source.main_config import DOWNLOAD_PATH
from db.crud_jmp import get_jmp_config
from sqlalchemy.sql.expression import true
from models.question import Question

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDownloaderUtil:
    @pytest.mark.asyncio
    async def test_generate_download_data(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        configs = get_jmp_config()
        computed_column_names = [cf["name"] for cf in configs]
        out_file = "testing_generate_download_file"
        job = {
            'id': 2,
            'status': 0,
            'payload': f"download-{out_file}.xlsx",
            'info': {
                'tags': [],
                'options': None,
                'province': None,
                'form_name': 'survey_questions',
                'school_type': None,
                'monitoring_round': None,
                'data_ids': None
            },
            'created': '2023-08-11',
            'available': None
        }

        # get PII questions
        questions = session.query(Question).filter(
            Question.personal_data == true()).all()
        question_names = [q.name for q in questions]

        file, context = generate_download_data(
            session=session,
            jobs=job,
            file=f"{DOWNLOAD_PATH}/{job.get('payload')}")

        result_file = f"{DOWNLOAD_PATH}/{job.get('payload')}"

        assert file == result_file
        df = pd.read_excel(result_file)
        columns = df.columns
        assert "id" not in columns
        # assert computed value in excel file
        for ccn in computed_column_names:
            assert ccn in columns
        # assert PII question not in excel file
        for qn in question_names:
            assert qn not in columns
