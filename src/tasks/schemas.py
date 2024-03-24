from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Tasks(BaseModel):
    task_id: int
    task_name: str
    description: Optional[str] = None
    status_id: int
    assigned_to: Optional[int] = None
    created_by: int
    project_id: int
    created_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

class TasksRequest(BaseModel):
    task_name: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    # created_by: int
    project_id: int



class UsersProjects(BaseModel):
    user_id: int
    project_id: int


class UsersProjectsResponse(BaseModel):
    user_id: int
    project_id: int
    description: str = None
    project_code: str = None
    created_by: int
