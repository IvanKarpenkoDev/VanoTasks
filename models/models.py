from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, \
    PrimaryKeyConstraint

metadata = MetaData()

role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON),
)

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("role_id", Integer, ForeignKey(role.c.id)),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)

task_statuses = Table(
    'task_statuses',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('status_name', String(50), unique=True, nullable=False)
)

profiles = Table(
    'profiles',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey(user.c.id), unique=True, nullable=False),
    Column('photo_url', String(255)),
    Column('full_name', String(100), nullable=False),
    Column('email', String(100), unique=True, nullable=False)
)

projects = Table(
    'projects',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String(100), unique=True, nullable=False),
    Column('description', String),  # You can specify the length of TEXT, or use String without length
    Column('project_code', String),
    Column('created_by', Integer, ForeignKey(user.c.id), nullable=False),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

user_projects = Table(
    'user_projects',
    metadata,
    Column('id', Integer, ForeignKey(user.c.id), nullable=False),
    Column('project_id', Integer, ForeignKey(projects.c.id), nullable=False),
    Column('role_id', Integer, ForeignKey(role.c.id)),
    PrimaryKeyConstraint('id', 'project_id')
)

tasks = Table(
    'tasks',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('task_name', String(100), nullable=False),
    Column('description', String),
    Column('status_id', Integer, ForeignKey(task_statuses.c.id), nullable=False, server_default='1'),
    Column('assigned_to', Integer, ForeignKey(user.c.id)),
    Column('created_by', Integer, ForeignKey(user.c.id), nullable=False),
    Column('project_id', Integer, ForeignKey(projects.c.id), nullable=False),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('due_date', TIMESTAMP)
)

task_comments = Table(
    'task_comments',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('task_id', Integer, ForeignKey(tasks.c.id), nullable=False),
    Column('commenter_id', Integer, ForeignKey(user.c.id), nullable=False),
    Column('comment_text', String, nullable=False),
    Column('commented_at', TIMESTAMP, default=datetime.utcnow)
)

task_status_history = Table(
    'task_status_history',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('task_id', Integer, ForeignKey(tasks.c.id), nullable=False),
    Column('old_status_id', Integer, ForeignKey(task_statuses.c.id)),
    Column('new_status_id', Integer, ForeignKey(task_statuses.c.id), nullable=False),
    Column('changed_by', Integer, ForeignKey(user.c.id), nullable=False),
    Column('change_time', TIMESTAMP, nullable=False)
)
