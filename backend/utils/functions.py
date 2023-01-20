from sqlalchemy import text
from db.connection import engine


def refresh_materialized_data():
    engine.execute(text("""
        REFRESH MATERIALIZED VIEW advance_filter;
    """))
