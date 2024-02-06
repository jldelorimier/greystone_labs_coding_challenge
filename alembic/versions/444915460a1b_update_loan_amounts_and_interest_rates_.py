"""Update Loan amounts and interest rates to Decimal values for precision rather than floats

Revision ID: 444915460a1b
Revises: 8bfbe5823b08
Create Date: 2024-02-06 16:24:36.249170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '444915460a1b'
down_revision: Union[str, None] = '8bfbe5823b08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table('loan') as batch_op:
        batch_op.alter_column('amount',
                  existing_type=sa.FLOAT(),
                  type_=sa.Numeric(precision=18, scale=6),
                  nullable=False)
        batch_op.alter_column('annual_interest_rate',
                  existing_type=sa.FLOAT(),
                  type_=sa.Numeric(precision=8, scale=5),
                  nullable=False)


def downgrade():
    with op.batch_alter_table('loan') as batch_op:
        batch_op.alter_column('annual_interest_rate',
                  existing_type=sa.Numeric(precision=8, scale=5),
                  type_=sa.FLOAT(),
                  nullable=False)
        batch_op.alter_column('amount',
                  existing_type=sa.Numeric(precision=18, scale=6),
                  type_=sa.FLOAT(),
                  nullable=False)
        