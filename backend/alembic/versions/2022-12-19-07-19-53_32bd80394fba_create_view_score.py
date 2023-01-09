"""create_view_score

Revision ID: 32bd80394fba
Revises: c72dc112b166
Create Date: 2022-12-19 07:19:53.255962

"""
from alembic import op
from alembic_utils.pg_materialized_view import PGMaterializedView

# revision identifiers, used by Alembic.
revision = "32bd80394fba"
down_revision = "c72dc112b166"
branch_labels = None
depends_on = None

score_view = PGMaterializedView(
    schema="public",
    signature="score_view",
    definition="""
    SELECT dd.id as data, scores.question,
    coalesce(scores.name, null) as option,
    coalesce(scores.score,null) as score
    FROM
    (
        SELECT a.data, a.question, o.name, o.score FROM answer a
        INNER join question q on a.question = q.id
        LEFT JOIN data d ON a.data = d.id
        LEFT JOIN option o ON a.question = o.question
        AND LOWER(a.options[1]) = LOWER(o.name)
        AND d.datapoint_id is NOT NULL
        WHERE q.type = 'option'
    ) scores
    RIGHT JOIN data dd on scores.data = dd.id
    WHERE dd.registration = False
    AND scores.score is NOT NULL;
    """,
)


def upgrade() -> None:
    op.create_entity(score_view)


def downgrade() -> None:
    op.drop_entity(score_view)
