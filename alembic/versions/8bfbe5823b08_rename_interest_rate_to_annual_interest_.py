"""Rename interest_rate to annual_interest_rate

Revision ID: 8bfbe5823b08
Revises: 16dd137a0011
Create Date: 2024-02-06 12:22:10.377685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bfbe5823b08'
down_revision: Union[str, None] = '16dd137a0011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('loan', 'interest_rate', new_column_name='annual_interest_rate')


def downgrade() -> None:
    op.alter_column('loan', 'annual_interest_rate', new_column_name='interest_rate')
