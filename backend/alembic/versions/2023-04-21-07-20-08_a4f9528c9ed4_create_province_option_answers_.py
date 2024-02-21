"""create province option answers materialize view

Revision ID: a4f9528c9ed4
Revises: 6e5704463f92
Create Date: 2023-04-21 07:20:08.294875

"""
from alembic import op
from alembic_utils.pg_materialized_view import PGMaterializedView


# revision identifiers, used by Alembic.
revision = "a4f9528c9ed4"
down_revision = "6e5704463f92"
branch_labels = None
depends_on = None

province_option_answers = PGMaterializedView(
    schema="public",
    signature="province_option_answer",
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
            UNNEST(a.options) as value,
            count(a.data)
        FROM answer a
        LEFT JOIN data d on a.data = d.id
        LEFT JOIN question q ON a.question = q.id
        WHERE q.type = 'option' OR q.type = 'multiple_option'
        GROUP BY
            a.options, a.question, q.type, q.form,
            d.current, d.year_conducted, province
        ORDER BY d.current DESC
    ) tmp;
    """,
)


def upgrade() -> None:
    op.create_entity(province_option_answers)
    pass


def downgrade() -> None:
    op.drop_entity(province_option_answers)
    pass
