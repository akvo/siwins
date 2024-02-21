"""add current column to data table

Revision ID: 9e35c2fdcc93
Revises: 4f61185284b5
Create Date: 2023-04-20 01:30:48.872281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9e35c2fdcc93"
down_revision = "4f61185284b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("data", sa.Column("current", sa.Boolean(), nullable=True))
    op.execute("UPDATE data SET current = false")
    op.alter_column("data", "current", nullable=False)


def downgrade() -> None:
    op.drop_column("data", "current")
