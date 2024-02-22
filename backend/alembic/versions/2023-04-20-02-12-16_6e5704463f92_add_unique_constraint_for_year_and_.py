"""add unique constraint for year and school to data table

Revision ID: 6e5704463f92
Revises: 9e35c2fdcc93
Create Date: 2023-04-20 02:12:16.920905

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "6e5704463f92"
down_revision = "9e35c2fdcc93"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_data_year_school", "data", ["year_conducted", "school_information"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_data_year_school", "data")
