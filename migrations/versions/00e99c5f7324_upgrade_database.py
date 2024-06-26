"""Upgrade database

Revision ID: 00e99c5f7324
Revises: d90f76818259
Create Date: 2024-04-10 16:44:43.048764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00e99c5f7324'
down_revision: Union[str, None] = 'd90f76818259'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('file_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'file_url')
    # ### end Alembic commands ###
