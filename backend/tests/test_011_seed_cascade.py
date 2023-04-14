import os
import sys
import json
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from seeder.cascade import seed_cascade
from source.main_config import QuestionConfig, CascadeLevels
from source.main_config import FORM_CONFIG_PATH
from db import crud_cascade

sys.path.append("..")
pytestmark = pytest.mark.asyncio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


school_information_qid = QuestionConfig.school_information.value
school_information_levels = CascadeLevels.school_information.value


forms = []
with open(FORM_CONFIG_PATH) as json_file:
    forms = json.load(json_file)


class TestSeedAndSync:
    @pytest.mark.asyncio
    async def test_seed_cascade(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        seed_cascade(session=session, forms=forms)
        cascade = crud_cascade.get_all_cascade(session=session)
        assert len(cascade) > 0
        cascade = crud_cascade.get_cascade_by_question_id(
            session=session, question=school_information_qid)
        assert len(cascade) > 0
        for k, level in school_information_levels.items():
            cascade = crud_cascade.get_cascade_by_question_id(
                session=session,
                question=school_information_qid,
                level=level)
            assert len(cascade) > 0
