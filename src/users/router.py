import boto3
from async_lru import alru_cache
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import current_user
from src.auth.models import user
from src.auth.schemas import UserRead
from src.database import get_async_session
from fastapi_pagination import Page, add_pagination, paginate

from src.users.models import profile
from src.users.shemas import Profile

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

s3_client = boto3.client('s3', endpoint_url='http://localhost:4566',
                         aws_access_key_id='VANO@GMAIL.COMasdasdasd',
                         aws_secret_access_key='IAMVANOasdasdas'
                         )


# @router.post("/upload-photo/")
# async def upload_photo(user_id: int, full_name: str, photo: UploadFile = File(...),
#                        session: AsyncSession = Depends(get_async_session), ):
#     try:
#         photo_data = await photo.read()
#         photo_key = f"profile_photos/{user_id}_{full_name}_{photo.filename}"
#         s3_client.put_object(Bucket='vano', Key=photo_key, Body=photo_data)
#
#         async for session in get_async_session():
#             query = update(profile).where(profile.c.user_id == user_id).values(
#                 photo_url=f"http://localhost:4566/vano/{photo_key}")
#             await session.execute(query)
#             await session.commit()
#
#         return {"message": "Photo uploaded successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error occurred during photo upload: {str(e)}")
@router.put("/upload/photo")
async def update_profile(user_id: int, full_name: str, photo: UploadFile = File(None),
                         session: AsyncSession = Depends(get_async_session)):
    try:
        if photo is not None:
            # Чтение данных фотографии
            photo_data = await photo.read()

            # Загрузка фотографии в хранилище
            photo_key = f"profile_photos/{user_id}_{full_name}_{photo.filename}"
            s3_client.put_object(Bucket='vano', Key=photo_key, Body=photo_data)

            photo_url = f"http://localhost:4566/vano/{photo_key}"
        else:
            photo_url = None

        async with session.begin():
            # Обновление данных профиля в базе данных
            query = (
                update(profile)
                .where(profile.c.user_id == user_id)
                .values(full_name=full_name)
            )

            # If photo is not None, include photo_url in the update query
            if photo_url is not None:
                query = query.values(photo_url=photo_url)

            await session.execute(query)

        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred during profile update: {str(e)}")


@router.get("/profile/{user_id}")
@alru_cache(maxsize=32)
async def get_user_profile(user_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        async with session.begin():
            query = select(profile).where(profile.c.user_id == user_id)
            result = await session.execute(query)
            user_profile = result.fetchone()

            if not user_profile:
                raise HTTPException(status_code=404, detail="User profile not found")

            photo_url = user_profile.photo_url

        return {"user_id": user_profile.user_id, "full_name": user_profile.full_name, "photo_url": photo_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while fetching user profile: {str(e)}")


@router.get("/all/profile", response_model=Page[Profile])
@alru_cache(maxsize=32)
async def get_all_profiles(session: AsyncSession = Depends(get_async_session)):
    query = select(profile)
    result = await session.execute(query)
    print(result)

    return paginate(result.fetchall())


@router.get("/", response_model=Page[UserRead])
@alru_cache(maxsize=32)
async def get_all_users(session: AsyncSession = Depends(get_async_session)):
    query = select(user)
    result = await session.execute(query)
    users = result.fetchall()
    return paginate(users)


@router.get("/id", response_model=UserRead)
@alru_cache(maxsize=32)
async def get_user_by_id(id: int = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(user).where(user.c.id == id.id)
    result = await session.execute(query)
    return result.first()


@router.get("/{id}", response_model=UserRead)
@alru_cache(maxsize=32)
async def get_user_by_id_not_cookie(id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(user).where(user.c.id == id)
    result = await session.execute(query)
    return result.first()


add_pagination(router)
