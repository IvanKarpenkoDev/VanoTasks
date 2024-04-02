from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import add_pagination, Page, paginate
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from sqlalchemy import select, func, join, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.auth.base_config import current_user
from src.database import get_async_session
from src.projects.models import projects
from src.tasks.models import tasks, task_comments, task_statuses
from src.tasks.schemas import Tasks, TasksRequest, TaskComments, TaskCommentsRequest, TaskStatuses, TasksCharts, \
    TasksWithName
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

sender_email = "testmailasp@mail.ru"
sender_password = "eJrai4Xtxvs78s4gQzBd"
receiver_email = "ihapaz12345@gmail.com"


def send_email(sender_email, sender_password, receiver_email, subject, message):
    try:
        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as smtp:
            smtp.login(sender_email, sender_password)

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            smtp.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")


sender_email = "testmailasp@mail.ru"
sender_password = "eJrai4Xtxvs78s4gQzBd"
receiver_email = "ihapaz12345@gmail.com"
subject = "VanoTasksLogger"


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


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(task_id: int, updated_task: TasksRequest, session: AsyncSession = Depends(get_async_session),
                      user=Depends(current_user)):
    try:
        task_query = select(tasks).where(tasks.c.task_id == task_id)
        task_result = await session.execute(task_query)
        existing_task = task_result.scalar_one_or_none()

        if existing_task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        update_values = {
            "task_name": updated_task.task_name,
            "description": updated_task.description,
            "assigned_to": updated_task.assigned_to,
            "project_id": updated_task.project_id
        }

        await session.execute(
            tasks.update().where(tasks.c.task_id == task_id).values(**update_values)
        )

        await session.commit()

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad request')


@router.get("/{task_id}", response_model=TasksWithName)
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
                           projects.project_name AS project_name
                    FROM tasks
                    JOIN projects ON tasks.project_id = projects.id
                    WHERE tasks.task_id = :task_id
                    """
        ).bindparams(task_id=task_id)
        result = await session.execute(query)
        task = result.first()
        print(task)

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        # access_message = (f'GET task: '
        #                   f'task_id: {task_id}')
        # send_email(sender_email, sender_password, receiver_email, subject, access_message)

        return task

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=Page[TasksWithName])
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


@router.get("/user_tasks/user_id", response_model=list[Tasks])
async def get_users_tasks_by_user_user_id(user_id: int = Depends(current_user),
                                          session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(tasks).where(tasks.c.assigned_to == user_id.id or tasks.c.created_by == user_id.id)
        result = await session.execute(query)
        return result.all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/charts/user_id", response_model=TasksCharts)
async def get_user_charts_tasks(user_id: int = Depends(current_user),
                                session: AsyncSession = Depends(get_async_session)):
    try:
        query_open = select(func.count()).where(tasks.c.assigned_to == user_id.id,
                                                tasks.c.status_id == 1)
        result = await session.execute(query_open)
        open = result.scalar_one_or_none(),
        query_in_progress = select(tasks).where(tasks.c.assigned_to == user_id.id,
                                                tasks.c.status_id == 2)
        result_in_progress = await session.execute(query_in_progress)
        in_progress = result_in_progress.scalar_one_or_none()
        query_close = select(tasks).where(tasks.c.assigned_to == user_id.id,
                                          tasks.c.status_id == 3)
        result_close = await session.execute(query_close)
        close = result_close.scalar_one_or_none()
        response = {
            'open': open[0] if open is not None else 0,
            'in_progress': in_progress[0] if in_progress is not None else 0,
            'close': close[0] if close is not None else 0,
        }

        return response
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


@router.get("/task_comments/{task_id}", response_model=list[TaskComments])
async def get_task_comments_by_task_id(task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(task_comments).where(tasks.c.task_id == task_id)
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


add_pagination(router)
