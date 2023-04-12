"""create administration table

Revision ID: 40164b45b0be
Revises: d37375e79c27
Create Date: 2023-03-17 02:24:00.321072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40164b45b0be'
down_revision = 'd37375e79c27'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'administration',
        sa.Column('id', sa.Integer()),
        sa.Column('parent', sa.Integer(), nullable=True),
        sa.Column('name', sa.String()),
        sa.PrimaryKeyConstraint(('id')))
    op.create_foreign_key(
        None, 'administration', 'administration',
        ['parent'], ['id'])
    op.create_index(
        op.f('ix_administration_id'),
        'administration', ['id'],
        unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_administration_id"), table_name="administration")
    op.drop_table('administration')
