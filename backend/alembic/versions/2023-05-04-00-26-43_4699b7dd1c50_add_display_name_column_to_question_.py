"""add display name column to question group table

Revision ID: 4699b7dd1c50
Revises: 3d72efcb5d98
Create Date: 2023-05-04 00:26:43.106554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4699b7dd1c50'
down_revision = '3d72efcb5d98'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "question_group", sa.Column(
            "display_name",
            sa.String(), nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column("question_group", "display_name")
