"""create data answers materialize view

Revision ID: b93bf26ef76a
Revises: 4699b7dd1c50
Create Date: 2023-05-08 08:27:40.049549

"""
from alembic import op
from alembic_utils.pg_materialized_view import PGMaterializedView


# revision identifiers, used by Alembic.
revision = 'b93bf26ef76a'
down_revision = '4699b7dd1c50'
branch_labels = None
depends_on = None

data_answers = PGMaterializedView(
    schema="public",
    signature="data_answers",
    definition="""
    select
        tmp.id,
        tmp.identifier,
        tmp.name,
        tmp.geo,
        tmp.created,
        json_agg(
            json_build_object(
                concat(tmp.qid, '|', tmp.qname),
                case
                    when tmp.qtype = 'number'
                        then (tmp.value::numeric)::text
                    when tmp.qtype = 'option'
                        or tmp.qtype = 'multiple_option'
                        or tmp.qtype = 'cascade'
                        then array_to_string(tmp.options, ', ')
                    else tmp.text
                end
            )
        ) as answers
    from (
        select
            d.id,
            d.identifier,
            d.name,
            array_to_string(d.geo, '|') as geo,
            d.created,
            q.id as qid,
            q.name as qname,
            q.type as qtype,
            a.value,
            a.options,
            a.text
        from answer a
        left join data d on a.data = d.id
        left join question q on a.question = q.id
        left join question_group qg on q.question_group = qg.id
        order by d.id, qg.order, q.order
    ) as tmp
    group by
        tmp.id,
        tmp.identifier,
        tmp.name,
        tmp.geo,
        tmp.created
    order by tmp.id;
    """,
)


def upgrade() -> None:
    op.create_entity(data_answers)
    pass


def downgrade() -> None:
    op.drop_entity(data_answers)
    pass
