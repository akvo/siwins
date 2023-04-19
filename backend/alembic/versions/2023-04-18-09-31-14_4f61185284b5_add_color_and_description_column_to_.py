"""add color and description column to option table

Revision ID: 4f61185284b5
Revises: 6ce5e096f642
Create Date: 2023-04-18 09:31:14.380569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f61185284b5'
down_revision = '6ce5e096f642'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "option", sa.Column(
            "color",
            sa.String(), nullable=True
        )
    )
    op.add_column(
        "option", sa.Column(
            "description",
            sa.Text(), nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column("option", "color")
    op.drop_column("option", "description")
