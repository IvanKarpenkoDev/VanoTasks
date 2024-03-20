from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, ForeignKey

from src.auth.models import user

metadata = MetaData()

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

