"""Upgrade database

Revision ID: 31f69c36e9dd
Revises: d712c8e51216
Create Date: 2024-03-23 16:05:00.886140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31f69c36e9dd'
down_revision: Union[str, None] = 'd712c8e51216'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_statuses',
    sa.Column('status_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('status_id'),
    sa.UniqueConstraint('status_name')
    )
    op.create_table('tasks',
    sa.Column('task_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=False),
    sa.Column('assigned_to', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('due_date', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['assigned_to'], ['user.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['status_id'], ['task_statuses.status_id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    # ### end Alembic commands ###
    op.execute(
        """
        INSERT INTO task_statuses (status_name) VALUES 
        ('Открыта'),
        ('В работе'),
        ('Закрыта');
        """
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    op.drop_table('task_statuses')
    op.execute(
        """
        DELETE FROM task_statuses WHERE status_name IN ('Открыта', 'В работе', 'Закрыта');
        """
    )
    # ### end Alembic commands ###