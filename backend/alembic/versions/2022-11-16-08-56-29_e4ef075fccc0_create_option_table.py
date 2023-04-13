"""create option table

Revision ID: e4ef075fccc0
Revises: 81e73c97498b
Create Date: 2022-11-16 08:56:29.694788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4ef075fccc0"
down_revision = "81e73c97498b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "option",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), default=None),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("name", sa.String()),
        sa.Column("question", sa.BigInteger(), sa.ForeignKey("question.id")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["question"],
            ["question.id"],
            name="question_option_constraint",
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_option_id"), "option", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_option_id"), table_name="option")
    op.drop_table("option")
