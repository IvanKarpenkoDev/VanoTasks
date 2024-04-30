import boto3
from async_lru import alru_cache
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi_pagination import add_pagination, Page, paginate
from logger import logger
from sqlalchemy import select, func, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.auth.base_config import current_user
from src.database import get_async_session
from src.tasks.models import tasks, task_comments, task_statuses
from src.tasks.schemas import Tasks, TaskComments, TaskCommentsRequest, TaskStatuses, TasksCharts, \
    TasksWithName
from fastapi import Form

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def create_task(task_name: str = Form(...), description: str = Form(...),
                      assigned_to: int = Form(...), project_id: int = Form(...),
                      photo: UploadFile = File(None),
                      session: AsyncSession = Depends(get_async_session),
                      user=Depends(current_user)):
    try:
        new_task = tasks.insert().values(
            task_name=task_name,
            description=description,
            assigned_to=assigned_to,
            created_by=user.id,
            project_id=project_id,
        )

        await session.execute(new_task)
        await session.commit()

        # Если есть файл, обновляем ссылку на файл в базе данных
        if photo is not None:
            # Получаем ID только что созданной задачи
            task_id = (await session.execute(select(func.max(tasks.c.task_id)))).scalar()

            # Обновляем ссылку на файл
            await update_file(task_id, photo, session=session)

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad request')


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(task_id: int, task_name: str = Form(...), description: str = Form(...),
                      assigned_to: int = Form(...), project_id: int = Form(...),
                      photo: UploadFile = File(None),
                      session: AsyncSession = Depends(get_async_session),
                      user=Depends(current_user)):
    try:
        task_query = select(tasks).where(tasks.c.task_id == task_id)
        task_result = await session.execute(task_query)
        existing_task = task_result.scalar_one_or_none()

        if existing_task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        update_values = {
            "task_name": task_name,
            "description": description,
            "assigned_to": assigned_to,
            "project_id": project_id
        }

        # Если есть файл, обновляем ссылку на файл в базе данных
        if photo is not None:
            await update_file(task_id, photo, session=session)

        await session.execute(
            tasks.update().where(tasks.c.task_id == task_id).values(**update_values)
        )

        await session.commit()

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad request')


@router.get("/{task_id}", response_model=TasksWithName)
@alru_cache(maxsize=32)
async def get_task_by_id(task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = text(
            f"""
                    SELECT tasks.task_id,
                           tasks.task_name,
                           tasks.description,
                           tasks.status_id,
                           tasks.assigned_to,
                           tasks.created_by,
                           tasks.project_id,
                           tasks.created_at,
                           tasks.due_date,
                           tasks.file_url,
                           projects.project_name AS project_name
                    FROM tasks
                    JOIN projects ON tasks.project_id = projects.id
                    WHERE tasks.task_id = :task_id
                    """
        ).bindparams(task_id=task_id)
        result = await session.execute(query)
        task = result.first()

        if task is None:
            logger.error('Task not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=Page[TasksWithName])
@alru_cache(maxsize=32)
async def get_all_tasks(session: AsyncSession = Depends(get_async_session)):
    try:
        query = text(
            f"""
                            SELECT tasks.task_id,
                                   tasks.task_name,
                                   tasks.description,
                                   tasks.status_id,
                                   tasks.assigned_to,
                                   tasks.created_by,
                                   tasks.project_id,
                                   tasks.created_at,
                                   tasks.due_date,
                                    tasks.file_url,
                                   projects.project_name AS project_name
                            FROM tasks
                            JOIN projects ON tasks.project_id = projects.id
                            """
        )
        result = await session.execute(query)
        return paginate(result.fetchall())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(task_id: int, session: AsyncSession = Depends(get_async_session)):
    delete_query = tasks.delete().where(tasks.c.task_id == task_id)
    await session.execute(delete_query)
    await session.commit()


@router.get("/user_tasks/{user_id}", response_model=list[Tasks])
async def get_users_tasks_by_user_user_id(user_id: int,
                                          session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(tasks).where(tasks.c.assigned_to == user_id or tasks.c.created_by == user_id)
        result = await session.execute(query)
        return result.all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/charts/{user_id}", response_model=TasksCharts)
@alru_cache(maxsize=32)
async def get_user_charts_tasks(user_id: int,
                                session: AsyncSession = Depends(get_async_session)):
    try:
        query_open = select(func.count()).where(tasks.c.assigned_to == user_id,
                                                tasks.c.status_id == 1)
        result_open = await session.execute(query_open)
        open_tasks = result_open.scalar_one_or_none()
        query_in_progress = select(func.count()).where(tasks.c.assigned_to == user_id,
                                                       tasks.c.status_id == 2)
        result_in_progress = await session.execute(query_in_progress)
        in_progress = result_in_progress.scalar_one_or_none()

        query_close = select(func.count()).where(tasks.c.assigned_to == user_id,
                                                 tasks.c.status_id == 3)
        result_close = await session.execute(query_close)
        close = result_close.scalar_one_or_none()
        response = {
            'open': open_tasks if open_tasks is not None else 0,
            'in_progress': in_progress if in_progress is not None else 0,
            'close': close if close is not None else 0,
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/project/charts/{project_id}", response_model=TasksCharts)
@alru_cache(maxsize=32)
async def get_user_charts_tasks(project_id: int,
                                session: AsyncSession = Depends(get_async_session)):
    try:
        query_open = select(func.count()).where(tasks.c.project_id == project_id,
                                                tasks.c.status_id == 1)
        result_open = await session.execute(query_open)
        open_tasks = result_open.scalar_one_or_none()
        query_in_progress = select(func.count()).where(tasks.c.project_id == project_id,
                                                       tasks.c.status_id == 2)
        result_in_progress = await session.execute(query_in_progress)
        in_progress = result_in_progress.scalar_one_or_none()

        query_close = select(func.count()).where(tasks.c.project_id == project_id,
                                                 tasks.c.status_id == 3)
        result_close = await session.execute(query_close)
        close = result_close.scalar_one_or_none()
        response = {
            'open': open_tasks if open_tasks is not None else 0,
            'in_progress': in_progress if in_progress is not None else 0,
            'close': close if close is not None else 0,
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/project_tasks/{project_id}", response_model=list[Tasks])
@alru_cache(maxsize=32)
async def get_tasks_by_project_id(project_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(tasks).where(tasks.c.project_id == project_id)
        result = await session.execute(query)
        return result.all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')


@router.get("/task_comments/{task_id}", response_model=list[TaskComments])
@alru_cache(maxsize=32)
async def get_task_comments_by_task_id(task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(task_comments).where(task_comments.c.task_id == task_id)
        result = await session.execute(query)
        return result.all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')


@router.post("/task_comments/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def create_task_comments(task_id: int, task_comments_body: TaskCommentsRequest,
                               session: AsyncSession = Depends(get_async_session),
                               user=Depends(current_user)):
    try:
        new_task = task_comments.insert().values(
            comment_text=task_comments_body.comment_text,
            task_id=task_id,
            commenter_id=user.id,
        )

        await session.execute(new_task)
        await session.commit()

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad request')


@router.put("/{task_id}/change_status/{new_status_id}", status_code=status.HTTP_200_OK)
async def change_task_status(task_id: int, new_status_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        task_query = select(tasks).where(tasks.c.task_id == task_id)
        task_result = await session.execute(task_query)
        task = task_result.scalar_one_or_none()

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        status_query = select(task_statuses).where(task_statuses.c.status_id == new_status_id)
        status_result = await session.execute(status_query)
        new_status = status_result.scalar_one_or_none()

        if new_status is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New status not found")

        update_query = tasks.update().where(tasks.c.task_id == task_id).values(status_id=new_status_id)
        await session.execute(update_query)
        await session.commit()

        return {"message": "Task status updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{task_id}/status", response_model=TaskStatuses)
@alru_cache(maxsize=32)
async def get_task_status(task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        task_query = select(tasks).where(tasks.c.task_id == task_id)
        task_result = await session.execute(task_query)
        task = task_result.first()

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        status_query = select(task_statuses).where(task_statuses.c.status_id == task.status_id)
        status_result = await session.execute(status_query)
        task_status = status_result.first()

        if task_status is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task status not found")

        return task_status

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


s3_client = boto3.client('s3', endpoint_url='http://localstack:4566',
                         aws_access_key_id='VANO@GMAIL.COMasdasdasd',
                         aws_secret_access_key='IAMVANOasdasdas'
                         )


# @router.put("/upload/file")
# async def update_file(task_id: int, photo: UploadFile = File(None),
#                       session: AsyncSession = Depends(get_async_session)):
#     try:
#         if photo is not None:
#             photo_data = await photo.read()
#
#             photo_key = f"tasks_photos/{task_id}_{photo.filename}"
#             s3_client.put_object(Bucket='file', Key=photo_key, Body=photo_data)
#
#             file_url = f"http://localstack:4566/file/{photo_key}"
#         else:
#             file_url = None
#
#         async with session.begin():
#             query = (
#                 update(tasks)
#                 .where(tasks.c.task_id == task_id)
#                 .values(file_url=file_url)
#             )
#
#             await session.execute(query)
#
#         return {"message": "Profile updated successfully"}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error occurred during profile update: {str(e)}")
async def update_file(task_id: int, photo: UploadFile = File(None),
                      session: AsyncSession = Depends(get_async_session)):
    try:
        if photo is not None:
            photo_data = await photo.read()

            photo_key = f"tasks_photos/{task_id}_{photo.filename}"
            s3_client.put_object(Bucket='file', Key=photo_key, Body=photo_data)

            file_url = f"http://localstack:4566/file/{photo_key}"
        else:
            file_url = None

        query = (
            update(tasks)
            .where(tasks.c.task_id == task_id)
            .values(file_url=file_url)
        )

        await session.execute(query)
        await session.commit()

        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred during profile update: {str(e)}")


add_pagination(router)
