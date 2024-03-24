"""Upgrade database

Revision ID: 305ff662cec0
Revises: 4d124a84f4e0
Create Date: 2024-03-23 15:04:29.143599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '305ff662cec0'
down_revision: Union[str, None] = '4d124a84f4e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'users_projects', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users_projects', type_='foreignkey')
    # ### end Alembic commands ###