"""add_materialize_view_for_advance_filter

Revision ID: e47196be4c5c
Revises: d37375e79c27
Create Date: 2023-01-10 07:24:50.778049

"""
from alembic import op
from alembic_utils.pg_materialized_view import PGMaterializedView


# revision identifiers, used by Alembic.
revision = "e47196be4c5c"
down_revision = "d37375e79c27"
branch_labels = None
depends_on = None

advance_filter_with_multiple_option_value = PGMaterializedView(
    schema="public",
    signature="advance_filter",
    definition="""
    SELECT tmp.data,
        array_agg(CONCAT(tmp.question, '||', lower(tmp.options))) as options
    FROM (
        SELECT a.data, a.question, a.id as answer_id,
        unnest(a.options) as options
        FROM answer a LEFT JOIN question q on q.id = a.question
        WHERE q.type = 'option'  or q.type = 'multiple_option'
    ) tmp GROUP BY tmp.data;
    """,
)


def upgrade():
    op.create_entity(advance_filter_with_multiple_option_value)
    pass


def downgrade():
    op.drop_entity(advance_filter_with_multiple_option_value)
    pass
