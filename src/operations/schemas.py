from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Projects(BaseModel):
    id: int
    project_name: str
    description: str = None
    project_code: str = None
    created_by: int
    created_at: Optional[datetime] = None


class UsersProjects(BaseModel):
    user_id: int
    project_id: int
    description: str = None
    project_code: str = None
    created_by: int
