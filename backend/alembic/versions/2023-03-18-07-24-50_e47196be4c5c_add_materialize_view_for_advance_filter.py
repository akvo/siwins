"""add_materialize_view_for_advance_filter

Revision ID: e47196be4c5c
Revises: 40164b45b0be
Create Date: 2023-03-18 07:24:50.778049

"""
from alembic import op
from alembic_utils.pg_materialized_view import PGMaterializedView


# revision identifiers, used by Alembic.
revision = "e47196be4c5c"
down_revision = "40164b45b0be"
branch_labels = None
depends_on = None

advance_filter_with_multiple_option_value = PGMaterializedView(
    schema="public",
    signature="advance_filter",
    definition="""
    SELECT 
	tmp.data,
	tmp.identifier,
	tmp.registration,
	tmp.form,
	array_agg(CONCAT(tmp.question, '||', lower(tmp.options))) as options
    FROM (
        SELECT 
            a.data, 
            a.question, 
            a.id as answer_id,
            unnest(a.options) as options,
            d.identifier,
            d.registration,
            d.form
        FROM answer a 
        LEFT JOIN question q on q.id = a.question
        LEFT JOIN data d on d.id = a.data
        WHERE q.type = 'option'  or q.type = 'multiple_option' 
    ) tmp GROUP BY tmp.data, tmp.identifier, tmp.registration, tmp.form;
    """,
)


def upgrade():
    op.create_entity(advance_filter_with_multiple_option_value)
    pass


def downgrade():
    op.drop_entity(advance_filter_with_multiple_option_value)
    pass
