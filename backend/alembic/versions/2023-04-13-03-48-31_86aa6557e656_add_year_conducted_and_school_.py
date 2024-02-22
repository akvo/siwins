"""add year conducted and school information into data table

Revision ID: 86aa6557e656
Revises: b3ad51d031c6
Create Date: 2023-04-13 03:48:31.786049

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision = "86aa6557e656"
down_revision = "b3ad51d031c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "data", sa.Column("year_conducted", sa.Integer(), nullable=True)
    )
    op.add_column(
        "data",
        sa.Column("school_information", pg.ARRAY(sa.String()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("data", "year_conducted")
    op.drop_column("data", "school_information")
