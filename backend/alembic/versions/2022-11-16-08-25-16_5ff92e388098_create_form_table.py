"""create form table

Revision ID: 5ff92e388098
Revises:
Create Date: 2022-11-16 08:25:16.988129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5ff92e388098"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "form",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String()),
        sa.Column("version", sa.Float(), nullable=True, default=0.0),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("registration_form", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["registration_form"],
            ["form.id"],
            name="form_registration_constraint",
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_form_id"), "form", ["id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_form_id"), table_name="form")
    op.drop_table("form")
