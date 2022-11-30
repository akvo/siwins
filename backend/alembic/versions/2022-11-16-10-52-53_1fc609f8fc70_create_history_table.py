"""create history table

Revision ID: 1fc609f8fc70
Revises: 04791db53e9f
Create Date: 2022-11-16 10:52:53.415817

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision = '1fc609f8fc70'
down_revision = '04791db53e9f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.BigInteger(), sa.ForeignKey('question.id')),
        sa.Column('data', sa.BigInteger(), sa.ForeignKey('data.id')),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('options', pg.ARRAY(sa.String()), nullable=True),
        sa.Column(
            'created', sa.DateTime(), nullable=True,
            server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column(
            'updated', sa.DateTime(), nullable=True,
            onupdate=sa.text('(CURRENT_TIMESTAMP)')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['question'], ['question.id'],
                                name='question_history_constraint',
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['data'], ['data.id'],
                                name='data_history_constraint',
                                ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_history_id'), 'history', ['id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_history_id'), table_name='history')
    op.drop_table('history')
