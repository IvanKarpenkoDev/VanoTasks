from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.base_config import current_user
from src.database import get_async_session
from src.operations.models import projects
from src.operations.schemas import Projects

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


@router.get("/{user_id}", response_model=list[Projects])
async def get_projects_by_user_id(user_id: int, session: AsyncSession = Depends(get_async_session),
                             user=Depends(current_user)):
    query = select(projects).where(projects.c.user_id == user_id)
    result = await session.execute(query)
    return result.all()

# @router.post("/")
# async def add_specific_operations(new_operation: OperationCreate, session: AsyncSession = Depends(get_async_session)):
#     stmt = insert(operation).values(**new_operation.dict())
#     await session.execute(stmt)
#     await session.commit()
#     return {"status": "success"}
