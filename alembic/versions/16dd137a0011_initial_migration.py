"""Initial migration

Revision ID: 16dd137a0011
Revises: 
Create Date: 2024-02-05 20:52:09.972595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16dd137a0011'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('loan') as batch_op:
      batch_op.drop_column('user_id')
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_email'), table_name='user')
    with op.batch_alter_table('loan') as batch_op:
      batch_op.add_column(sa.Column('user_id', sa.INTEGER(), nullable=False))
