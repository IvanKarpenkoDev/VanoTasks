from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from src.auth.models import user
from src.database import engine
from src.projects.models import projects

metadata = MetaData()


# Таблица статусов задач
task_statuses = Table(
    'task_statuses',
    metadata,
    Column('status_id', Integer, primary_key=True, autoincrement=True),
    Column('status_name', String(50), unique=True, nullable=False)
)


# Таблица задач
tasks = Table(
    'tasks',
    metadata,
    Column('task_id', Integer, primary_key=True, autoincrement=True),
    Column('task_name', String(100), nullable=False),
    Column('description', String(200)),
    Column('status_id', Integer, ForeignKey(task_statuses.c.status_id), nullable=False, default=1),
    Column('assigned_to', Integer, ForeignKey(user.c.id)),
    Column('created_by', Integer, ForeignKey(user.c.id), nullable=False),
    Column('project_id', Integer, ForeignKey(projects.c.id, ondelete='CASCADE'), nullable=False),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('due_date', TIMESTAMP, default=datetime.utcnow)
)

# -- Создание таблицы комментариев к задачам
# CREATE TABLE task_comments (
#     comment_id SERIAL PRIMARY KEY,
#     task_id INTEGER REFERENCES tasks(task_id) NOT NULL,
#     commenter_id INTEGER REFERENCES users(user_id) NOT NULL,
#     comment_text TEXT NOT NULL,
#     commented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
