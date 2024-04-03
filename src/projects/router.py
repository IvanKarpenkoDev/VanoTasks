from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate, add_pagination
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.auth.base_config import current_user
from src.auth.models import user
from src.auth.schemas import UserRead
from src.database import get_async_session
from src.projects.models import projects, users_projects
from src.projects.schemas import Projects, UsersProjectsResponse, ProjectsRequest, ProjectWithTaskCount
from src.tasks.models import tasks

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.get("/", response_model=Page[Projects])
async def get_all_projects(session: AsyncSession = Depends(get_async_session)):
    query = select(projects)
    result = await session.execute(query)

    return paginate(result.fetchall())


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def create_project(project: ProjectsRequest, session: AsyncSession = Depends(get_async_session),
                         user=Depends(current_user)):
    try:
        new_project = projects.insert().values(
            project_name=project.project_name,
            description=project.description,
            project_code=project.project_code,
            created_by=user.id,
        )

        await session.execute(new_project)
        await session.commit()

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad Request')


@router.get("/{id}", response_model=ProjectWithTaskCount)
async def get_project_with_task_count(id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        project_query = select(projects).where(projects.c.id == id)
        project_result = await session.execute(project_query)
        project = project_result.first()

        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        task_count_query = select(func.count()).where(tasks.c.project_id == id)
        task_count_result = await session.execute(task_count_query)
        task_count = task_count_result.first()

        return {"project": project, "task_count": int(task_count[0])}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_id(id: int, session: AsyncSession = Depends(get_async_session)):
    delete_query = projects.delete().where(projects.c.id == id)
    await session.execute(delete_query)
    await session.commit()


@router.get("/user_projects/{user_id}")
async def get_user_projects_by_user_id(user_id: int = Depends(current_user),
                                       session: AsyncSession = Depends(get_async_session)):
    query = (
        select(users_projects.c.user_id, users_projects.c.project_id, projects.c.id, projects.c.project_name,
               projects.c.description, projects.c.created_by)
        .join(projects, users_projects.c.project_id == projects.c.id)
        .where(users_projects.c.user_id == user_id.id)
    )
    result = await session.execute(query)
    projects_data = [
        {key: getattr(project, key) for key in project._fields}  # Access columns using getattr
        for project in result.all()
    ]
    projects1 = [UsersProjectsResponse(**project) for project in projects_data]
    return projects1


@router.post("/user_projects/{user_id}/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_user_project(user_id: int, project_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(users_projects.insert().values(user_id=user_id, project_id=project_id))
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User project already exists{e}")


@router.delete("/user_projects/{username}/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_project(username: str, project_id: int, session: AsyncSession = Depends(get_async_session)):
    user_query = select(user.c.id).where(user.c.username == username)
    user_result = await session.execute(user_query)
    user_row = user_result.first()
    if user_row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{username}' not found")

    delete_query = users_projects.delete().where(
        (users_projects.c.user_id == user_row.id) & (users_projects.c.project_id == project_id)
    )
    await session.execute(delete_query)
    await session.commit()


@router.get("/project_users/{project_id}", response_model=list[UserRead])
async def get_project_users(project_id: int, session: AsyncSession = Depends(get_async_session)):
    query = (
        select(user)
        .join(users_projects, user.c.id == users_projects.c.user_id)
        .where(users_projects.c.project_id == project_id)
    )
    result = await session.execute(query)

    return result.all()


add_pagination(router)
