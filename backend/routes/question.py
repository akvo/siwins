from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.security import HTTPBearer

# from fastapi.security import HTTPBasicCredentials as credentials
from typing import List
from sqlalchemy.orm import Session
from db import crud_question
from db.connection import get_session
from models.question import QuestionDictForFilter

security = HTTPBearer()
question_route = APIRouter()


@question_route.get(
    "/question/",
    response_model=List[QuestionDictForFilter],
    summary="get all questions",
    name="question:question_route_for_advance_filter",
    tags=["Question"],
)
def get(req: Request, session: Session = Depends(get_session)):
    question = crud_question.get_question_for_advance_filter(session=session)
    return [f.serialize_advance_filter for f in question]
