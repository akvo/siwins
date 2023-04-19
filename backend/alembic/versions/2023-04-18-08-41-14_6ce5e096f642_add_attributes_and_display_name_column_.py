"""add attributes and display name column to question table

Revision ID: 6ce5e096f642
Revises: 86aa6557e656
Create Date: 2023-04-18 08:41:14.869465

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision = '6ce5e096f642'
down_revision = '86aa6557e656'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "question", sa.Column(
            "attributes",
            pg.ARRAY(sa.String()), nullable=True
        )
    )
    op.add_column(
        "question", sa.Column(
            "display_name",
            sa.String(), nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column("question", "attributes")
    op.drop_column("question", "display_name")
