from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.base_config import current_user
from src.auth.models import user
from src.database import get_async_session
from src.operations.models import projects, users_projects
from src.operations.schemas import Projects, UsersProjects

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.get("/", response_model=list[Projects])
async def get_all_projects(session: AsyncSession = Depends(get_async_session), user=Depends(current_user)):
    query = select(projects)
    result = await session.execute(query)
    return result.all()


@router.get("/{id}", response_model=Projects)
async def get_project_by_id(id: int, session: AsyncSession = Depends(get_async_session), user=Depends(current_user)):
    query = select(projects).where(projects.c.id == id)
    result = await session.execute(query)
    return result.first()


@router.get("/user_projects/{user_id}")
async def get_user_projects_by_user_id(user_id: int, session: AsyncSession = Depends(get_async_session), user=Depends(current_user)):
    query = (
        select(users_projects.c.user_id, users_projects.c.project_id, projects.c.id, projects.c.project_name,
               projects.c.description, projects.c.created_by)
        .join(projects, users_projects.c.project_id == projects.c.id)
        .where(users_projects.c.user_id == user_id)
    )
    result = await session.execute(query)
    # Convert data to UsersProjects objects (optional)
    projects_data = [
        {key: getattr(project, key) for key in project._fields}  # Access columns using getattr
        for project in result.all()
    ]

    projects1 = [UsersProjects(**project) for project in projects_data]
    print(projects1)
    return projects1
