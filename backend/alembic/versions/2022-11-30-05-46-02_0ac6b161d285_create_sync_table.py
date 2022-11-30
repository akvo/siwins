"""create sync table

Revision ID: 0ac6b161d285
Revises: 1fc609f8fc70
Create Date: 2022-11-30 05:46:02.317058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ac6b161d285'
down_revision = '1fc609f8fc70'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'sync',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text()),
        sa.Column(
            'created', sa.DateTime(), nullable=True,
            server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sync_id'), 'sync', ['id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_sync_id'), table_name='sync')
    op.drop_table('sync')
