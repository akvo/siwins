"""add_score_in_option

Revision ID: c72dc112b166
Revises: d37375e79c27
Create Date: 2022-12-19 07:03:48.848981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c72dc112b166'
down_revision = 'd37375e79c27'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('option', sa.Column('score', sa.Integer(), default=None))


def downgrade() -> None:
    op.drop_column('option', 'score')
