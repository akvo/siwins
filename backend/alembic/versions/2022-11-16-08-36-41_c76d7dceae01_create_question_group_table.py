"""create question group table

Revision ID: c76d7dceae01
Revises: 5ff92e388098
Create Date: 2022-11-16 08:36:41.288702

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision = 'c76d7dceae01'
down_revision = '5ff92e388098'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'question_group',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('order', sa.Integer(), default=None),
        sa.Column('name', sa.String()),
        sa.Column('form', sa.BigInteger(), sa.ForeignKey('form.id')),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column(
            'repeatable', sa.Boolean, server_default=expression.false(),
            nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['form'], ['form.id'],
                                name='form_question_group_constraint',
                                ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_question_group_id'),
                    'question_group', ['id'],
                    unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_question_group_id'), table_name='question_group')
    op.drop_table('question_group')
