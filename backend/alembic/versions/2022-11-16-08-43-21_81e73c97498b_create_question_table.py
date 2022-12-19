"""create question table

Revision ID: 81e73c97498b
Revises: c76d7dceae01
Create Date: 2022-11-16 08:43:21.353237

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision = "81e73c97498b"
down_revision = "c76d7dceae01"
branch_labels = None
depends_on = None


class CastingArray(pg.ARRAY):
    def bind_expression(self, bindvalue):
        return sa.cast(bindvalue, self)


def upgrade() -> None:
    op.create_table(
        "question",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("order", sa.Integer(), default=None),
        sa.Column("name", sa.String()),
        sa.Column("form", sa.BigInteger(), sa.ForeignKey("form.id")),
        sa.Column("type", sa.String()),
        sa.Column("meta", sa.Boolean(), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column(
            "question_group",
            sa.BigInteger(),
            sa.ForeignKey("question_group.id"),
        ),
        sa.Column("dependency", CastingArray(pg.JSONB()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["form"],
            ["form.id"],
            name="form_question_constraint",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_group"],
            ["question_group.id"],
            name="question_group_question_constraint",
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_question_id"), "question", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_question_id"), table_name="question")
    op.drop_table("question")
    op.execute("DROP TYPE questiontype")
