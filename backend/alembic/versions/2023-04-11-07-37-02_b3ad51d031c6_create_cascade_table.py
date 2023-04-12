"""create cascade table

Revision ID: b3ad51d031c6
Revises: e47196be4c5c
Create Date: 2023-04-11 07:37:02.793020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3ad51d031c6'
down_revision = 'e47196be4c5c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cascade',
        sa.Column('id', sa.Integer()),
        sa.Column('parent', sa.Integer(), nullable=True),
        sa.Column('name', sa.String()),
        sa.Column('level', sa.Integer()),
        sa.Column("question", sa.BigInteger(), sa.ForeignKey("question.id")),
        sa.PrimaryKeyConstraint(('id')),
        sa.ForeignKeyConstraint(
            ["question"],
            ["question.id"],
            name="question_cascade_constraint",
            ondelete="CASCADE",
        ))
    op.create_foreign_key(
        None, 'cascade', 'cascade',
        ['parent'], ['id'])
    op.create_index(
        op.f('ix_cascade_id'),
        'cascade', ['id'],
        unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_cascade_id"), table_name="cascade")
    op.drop_table('cascade')
