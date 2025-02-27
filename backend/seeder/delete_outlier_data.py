from sqlalchemy.orm import Session
from sqlalchemy import func, select
from models.data import Data


def delete_outlier_schools(session: Session):
    """
    Purpose:
    To make the data balance between the monitoring round,
    which mean we only include or keep the data that only
    have year_conducted for both monitoring round (2018, 2024).
    """
    # Get records where school_information appears only once
    subquery = (
        select(Data.school_information)
        .group_by(Data.school_information)
        .having(func.count(Data.year_conducted) == 1)
        .scalar_subquery()
    )

    # Get Data IDs that match the filtered school_information values
    data_ids = (
        session.query(Data.id)
        .filter(Data.school_information.in_(subquery))
        .all()
    )
    data_ids = [d[0] for d in data_ids]

    if data_ids:
        session.query(Data).filter(Data.id.in_(data_ids)).delete(
            synchronize_session=False
        )
        session.commit()
