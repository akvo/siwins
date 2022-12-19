"""create answer table

Revision ID: 04791db53e9f
Revises: 8e63db7aacb7
Create Date: 2022-11-16 10:51:46.293830

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision = "04791db53e9f"
down_revision = "8e63db7aacb7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "answer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question", sa.BigInteger(), sa.ForeignKey("question.id")),
        sa.Column("data", sa.BigInteger(), sa.ForeignKey("data.id")),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("options", pg.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.Column(
            "updated",
            sa.DateTime(),
            nullable=True,
            onupdate=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["question"],
            ["question.id"],
            name="question_answer_constraint",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["data"],
            ["data.id"],
            name="data_answer_constraint",
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_answer_id"), "answer", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_answer_id"), table_name="answer")
    op.drop_table("answer")
