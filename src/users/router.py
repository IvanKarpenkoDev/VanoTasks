from fastapi import APIRouter, Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import user
from src.auth.schemas import UserRead
from src.database import get_async_session

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=list[UserRead])
async def get_all_users(session: AsyncSession = Depends(get_async_session)):
    query = select(user)
    result = await session.execute(query)
    return result.all()


@router.get("/{id}", response_model=UserRead)
async def get_user_by_id(id: int = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(user).where(user.c.id == id.id)
    result = await session.execute(query)
    return result.first()
