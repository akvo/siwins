"""create data table

Revision ID: 8e63db7aacb7
Revises: e4ef075fccc0
Create Date: 2022-11-16 09:11:04.113127

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision = "8e63db7aacb7"
down_revision = "e4ef075fccc0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("datapoint_id", sa.BigInteger(), nullable=True),
        sa.Column("identifier", sa.String(), nullable=True),
        sa.Column("name", sa.String()),
        sa.Column("form", sa.BigInteger(), sa.ForeignKey("form.id")),
        sa.Column("registration", sa.Boolean(), nullable=False),
        sa.Column("geo", pg.ARRAY(sa.Float()), nullable=True),
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
            ["form"],
            ["form.id"],
            name="form_data_constraint",
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_data_id"), "data", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_data_id"), table_name="data")
    op.drop_table("data")
