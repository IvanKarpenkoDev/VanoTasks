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

class TasksWithName(BaseModel):
    task_id: int
    task_name: str
    description: Optional[str] = None
    status_id: int
    assigned_to: Optional[int] = None
    created_by: int
    project_id: int
    project_name: str
    created_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

class TasksWithProjectName(Tasks):
    project_name: str

class TasksCharts(BaseModel):
    open: int
    in_progress: int
    close: int


class TasksRequest(BaseModel):
    task_name: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    # created_by: int
    project_id: int


class TaskComments(BaseModel):
    comment_text: str
    task_id: int
    commenter_id: int
    commented_at: Optional[datetime] = None


class TaskCommentsRequest(BaseModel):
    comment_text: str


class TaskStatuses(BaseModel):
    status_id: int
    status_name: str
