"""add personal data column to question table

Revision ID: bb1391a4aedf
Revises: df4686198763
Create Date: 2023-08-10 05:15:08.524094

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb1391a4aedf'
down_revision = 'df4686198763'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "question",
        sa.Column("personal_data", sa.Boolean(), nullable=True)
    )
    op.execute("UPDATE question SET personal_data = false")
    op.alter_column("question", "personal_data", nullable=False)


def downgrade() -> None:
    op.drop_column("question", "personal_data")
