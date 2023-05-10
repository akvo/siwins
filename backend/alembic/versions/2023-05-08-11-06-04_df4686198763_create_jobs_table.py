"""create jobs table

Revision ID: df4686198763
Revises: b93bf26ef76a
Create Date: 2023-05-08 11:06:04.398375

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision = 'df4686198763'
down_revision = 'b93bf26ef76a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'jobs',
        sa.Column(
            'id', sa.Integer()),
        sa.Column(
            'status',
            sa.Integer(),
            server_default=sa.text('0::int')),
        sa.Column(
            'payload', sa.Text(), nullable=False),
        sa.Column(
            'info', pg.JSONB(), nullable=True),
        sa.Column(
            'created',
            sa.DateTime(),
            server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column(
            'available',
            sa.DateTime(),
            onupdate=sa.text('(CURRENT_TIMESTAMP)')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_jobs_id'), table_name='jobs')
    op.drop_table('jobs')
