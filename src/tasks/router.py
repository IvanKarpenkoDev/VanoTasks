from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.auth.base_config import current_user
from src.auth.models import user
from src.auth.schemas import UserRead
from src.database import get_async_session
from src.projects.models import projects, users_projects
from src.projects.schemas import Projects, UsersProjectsResponse
from src.tasks.models import tasks
from src.tasks.schemas import Tasks, TasksRequest

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def create_task(task: TasksRequest, session: AsyncSession = Depends(get_async_session),
                      user=Depends(current_user)):
    try:
        new_task = tasks.insert().values(
            task_name=task.task_name,
            description=task.description,
            assigned_to=task.assigned_to,
            created_by=user.id,
            project_id=task.project_id,
        )

        await session.execute(new_task)
        await session.commit()

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad request')


@router.get("/{task_id}", response_model=Tasks)
async def get_task_by_id(task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(tasks).where(tasks.c.task_id == task_id)
        result = await session.execute(query)
        task = result.first()
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/user_tasks/user_id", response_model=list[Tasks])
async def get_users_tasks_by_user_user_id(user_id: int = Depends(current_user),
                                     session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(tasks).where(tasks.c.assigned_to == user_id.id, tasks.c.created_by == user_id.id)
        result = await session.execute(query)
        return result.all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/project_tasks/{project_id}", response_model=list[Tasks])
async def get_tasks_by_project_id(project_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(tasks).where(tasks.c.project_id == project_id)
        result = await session.execute(query)
        return result.all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
