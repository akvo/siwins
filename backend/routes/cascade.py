from typing import List, Optional
from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from db.connection import get_session
from models.cascade import CascadeSimplified
from db import crud_cascade
from source.main_config import QuestionConfig, \
    SchoolInformationEnum, CascadeLevels

security = HTTPBearer()
cascade_route = APIRouter()

school_information_qid = QuestionConfig.school_information.value
school_information_levels = CascadeLevels.school_information.value


@cascade_route.get(
    "/cascade/school_information",
    response_model=List[CascadeSimplified],
    name="cascade:get_school_information",
    summary="get school information cascade of filter",
    tags=["Cascade"]
)
def get_cascade(
    req: Request,
    level: Optional[SchoolInformationEnum] = None,
    session: Session = Depends(get_session)
):
    level_numb = school_information_levels[level.value]
    cascade = crud_cascade.get_cascade_by_question_id(
        session=session,
        question=school_information_qid,
        level=level_numb)
    cascade = [c.simplify for c in cascade]
    return cascade
