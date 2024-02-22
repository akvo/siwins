"""create province number answers materialize view

Revision ID: 3d72efcb5d98
Revises: a4f9528c9ed4
Create Date: 2023-04-21 07:46:46.532092

"""
from alembic import op
from alembic_utils.pg_materialized_view import PGMaterializedView


# revision identifiers, used by Alembic.
revision = "3d72efcb5d98"
down_revision = "a4f9528c9ed4"
branch_labels = None
depends_on = None

province_number_answers = PGMaterializedView(
    schema="public",
    signature="province_number_answer",
    definition="""
    SELECT
        row_number() over (order by tmp.question) as id,
        *
    FROM (
        SELECT
            a.question, q.type, q.form,
            d.current, d.year_conducted,
            ARRAY_AGG(a.data) as data_ids,
            d.school_information[1] as province,
            SUM(a.value) as value,
            count(a.data)
        FROM answer a
        LEFT JOIN data d on a.data = d.id
        LEFT JOIN question q ON a.question = q.id
        WHERE q.type =  'number'
        GROUP BY
            a.question, q.type, q.form,
            d.current, d.year_conducted, province
        ORDER BY d.current DESC
    ) tmp;
    """,
)


def upgrade() -> None:
    op.create_entity(province_number_answers)
    pass


def downgrade() -> None:
    op.drop_entity(province_number_answers)
    pass
