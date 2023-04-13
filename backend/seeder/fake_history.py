import random
from db import crud_form, crud_option, crud_answer
from faker import Faker
from sqlalchemy.orm import Session
from datetime import datetime
from models.answer import Answer
from models.question import QuestionType
from models.data import DataDict
from models.history import History


def generate_fake_history(session: Session, datapoint: DataDict):
    forms = crud_form.get_monitoring_form(session=session)
    fake = Faker()
    for form in forms:
        for qg in form.question_group:
            for q in qg.question:
                answer = Answer(question=q.id, created=datetime.now())
                aval = None
                # TODO :: Need to update answer, generate for all question type
                if q.type in [
                    QuestionType.option,
                    QuestionType.multiple_option,
                ]:
                    options = crud_option.get_option_by_question_id(
                        session=session, question=q.id
                    )
                    fa = random.choice(options)
                    aval = [{"text": fa.name}]
                    answer.options = aval

                if q.type == QuestionType.number:
                    aval = fake.random_int(min=10, max=50)
                    answer.value = aval

                if q.type == QuestionType.text:
                    aval = fake.company()
                    answer.text = aval

                current_answers = crud_answer.get_answer_by_data_and_question(
                    session=session, data=datapoint.id, questions=[q.id]
                )

                if len(current_answers):
                    current_answer = current_answers[0]
                    # create history
                    history = History(
                        question=q.id,
                        data=datapoint.id,
                        text=current_answer.text,
                        value=current_answer.value,
                        options=current_answer.options,
                        created=current_answer.created,
                        updated=current_answer.updated,
                    )

                    # update current answer
                    update_answer = answer
                    update_answer.id = current_answer.id
                    update_answer.data = datapoint.id

                    crud_answer.update_answer(
                        session=session,
                        answer=update_answer,
                        history=history,
                        type=q.type,
                        value=aval,
                    )
