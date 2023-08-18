import sys
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session
from models.data import Data
from models.question import Question, QuestionType
# from tests.test_school_detail_popup_dump import (
#     res_school_detail_popup
# ) # TODO:: Delete

sys.path.append("..")
pytestmark = pytest.mark.asyncio


class TestDataDetailRoutes:
    @pytest.mark.asyncio
    async def test_get_data_detail(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        data = session.query(Data).first()
        res = await client.get(
            app.url_path_for("data:get_data_detail", data_id=data.id))
        assert res.status_code == 200
        res = res.json()
        assert list(res) == [
            'id', 'name',
            'year_conducted', 'school_information',
            'jmp_levels', 'answer'
        ]
        assert list(res["jmp_levels"][0]) == [
            'year', 'history', 'category', 'level', 'color'
        ]
        assert list(res["answer"][0]) == ['group', 'child']
        assert list(res["answer"][0]["child"][0]) == [
            'question_id', 'question_name',
            'render', 'history', 'year', 'value'
        ]
        for it in list(res["answer"][0]["child"]):
            if it["render"] == "chart":
                assert list(it["value"][0]) == [
                    'level', 'total', 'count', 'value'
                ]
        # TODO:: Delete
        # assert res == res_school_detail_popup

    @pytest.mark.asyncio
    async def test_get_answer_history(
        self, app: FastAPI, session: Session, client: AsyncClient
    ) -> None:
        data = session.query(Data).first()
        questions = session.query(Question)
        option_question = questions.filter(
            Question.type == QuestionType.option).first()
        number_question = questions.filter(
            Question.type == QuestionType.number).first()
        # no datapoint
        res = await client.get(
            app.url_path_for("answer:get_history", data_id=12345),
            params={'question_id': 640620926})
        assert res.status_code == 404
        # no question
        res = await client.get(
            app.url_path_for("answer:get_history", data_id=data.id),
            params={'question_id': 12345})
        assert res.status_code == 404
        # option question
        res = await client.get(
            app.url_path_for("answer:get_history", data_id=data.id),
            params={'question_id': option_question.id})
        assert res.status_code == 404
        # correct data
        res = await client.get(
            app.url_path_for("answer:get_history", data_id=data.id),
            params={'question_id': number_question.id})
        assert res.status_code == 200
        res = res.json()
        assert list(res[0]) == [
            'question_id', 'question_name', 'type',
            'history', 'year', 'value', 'render'
        ]
        assert list(res[0]["value"][0]) == [
            'level', 'total', 'count', 'value'
        ]
        # TODO:: Delete
        # assert res == [{
        #     'question_id': 624670928,
        #     'question_name': 'No. of classrooms',
        #     'type': 'number',
        #     'history': True,
        #     'year': 2018,
        #     'value': [{
        #         'level': 'AO CHS - 21710',
        #         'total': 12.0,
        #         'count': 1,
        #         'value': 12.0,
        #     }, {
        #         'level': 'Guadalcanal',
        #         'total': 12.0,
        #         'count': 1,
        #         'value': 12.0,
        #     }, {
        #         'level': 'National',
        #         'total': 12.0,
        #         'count': 1,
        #         'value': 12.0,
        #     }],
        #     'render': 'chart'
        # }]
