"""add meta geo column to question table

Revision ID: d37375e79c27
Revises: 0ac6b161d285
Create Date: 2022-12-13 08:45:56.804695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd37375e79c27'
down_revision = '0ac6b161d285'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'question',
        sa.Column('meta_geo', sa.Boolean(), nullable=True))
    op.execute("UPDATE question SET meta_geo = false")
    op.alter_column('question', 'meta_geo', nullable=False)


def downgrade() -> None:
    op.drop_column('question', 'meta_geo')
