from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from src.auth.models import user

metadata = MetaData()

profile = Table(
    'profile',
    metadata,
    Column('profile_id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey(user.c.id), nullable=False),
    Column('full_name', String(100), nullable=False),
    Column('photo_url', String, nullable=True),
)
