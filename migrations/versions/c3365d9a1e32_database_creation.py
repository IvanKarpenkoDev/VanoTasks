"""Database creation

Revision ID: c3365d9a1e32
Revises: 
Create Date: 2024-03-06 16:59:36.652106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3365d9a1e32'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('role_name', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('role_name')
    )
    op.create_table('task_statuses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('status_name', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('status_name')
    )
    op.create_table('user',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=50), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(), server_default='CURRENT_TIMESTAMP', nullable=False),
            sa.Column('role_id', sa.Integer(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.Column('is_superuser', sa.Boolean(), nullable=False),
            sa.Column('is_verified', sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email'),
            sa.UniqueConstraint('username')
    )
    op.create_table('profiles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('photo_url', sa.String(length=255), nullable=True),
            sa.Column('full_name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email'),
            sa.UniqueConstraint('user_id')
    )
    op.create_table('projects',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('project_name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('project_code', sa.String(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(), server_default='CURRENT_TIMESTAMP', nullable=False),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('project_name')
    )
    op.create_table('tasks',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('task_name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('status_id', sa.Integer(), server_default='1', nullable=False),
            sa.Column('assigned_to', sa.Integer(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.TIMESTAMP(), server_default='CURRENT_TIMESTAMP', nullable=False),
            sa.Column('due_date', sa.TIMESTAMP(), nullable=True),
            sa.ForeignKeyConstraint(['assigned_to'], ['user.id'], ),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
            sa.ForeignKeyConstraint(['status_id'], ['task_statuses.id'], ),
            sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_projects',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('role_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['id'], ['user.id'], ),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
            sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
            sa.PrimaryKeyConstraint('id', 'project_id')
    )
    op.create_table('task_comments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('task_id', sa.Integer(), nullable=False),
            sa.Column('commenter_id', sa.Integer(), nullable=False),
            sa.Column('comment_text', sa.String(), nullable=False),
            sa.Column('commented_at', sa.TIMESTAMP(), server_default='CURRENT_TIMESTAMP', nullable=False),
            sa.ForeignKeyConstraint(['commenter_id'], ['user.id'], ),
            sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
            sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_status_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('task_id', sa.Integer(), nullable=False),
            sa.Column('old_status_id', sa.Integer(), nullable=True),
            sa.Column('new_status_id', sa.Integer(), nullable=False),
            sa.Column('changed_by', sa.Integer(), nullable=False),
            sa.Column('change_time', sa.TIMESTAMP(), server_default='CURRENT_TIMESTAMP', nullable=False),
            sa.ForeignKeyConstraint(['changed_by'], ['user.id'], ),
            sa.ForeignKeyConstraint(['new_status_id'], ['task_statuses.id'], ),
            sa.ForeignKeyConstraint(['old_status_id'], ['task_statuses.id'], ),
            sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
            sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_status_history')
    op.drop_table('task_comments')
    op.drop_table('user_projects')
    op.drop_table('tasks')
    op.drop_table('projects')
    op.drop_table('profiles')
    op.drop_table('user')
    op.drop_table('task_statuses')
    op.drop_table('role')
    # ### end Alembic commands ###
