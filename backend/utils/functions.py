from sqlalchemy import text
from db.connection import engine


def refresh_materialized_view_query():
    return text("""
        REFRESH MATERIALIZED VIEW advance_filter;
        REFRESH MATERIALIZED VIEW province_option_answer;
    """)


def refresh_materialized_data():
    query = refresh_materialized_view_query()
    engine.execute(query)
