from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import add_pagination, Page, paginate
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.auth.base_config import current_user
from src.database import get_async_session
from src.tasks.models import tasks, task_comments
from src.tasks.schemas import Tasks, TasksRequest, TaskComments, TaskCommentsRequest
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


@router.get("/{task_id}", response_model=Tasks)
async def get_task_by_id(task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(tasks).where(tasks.c.task_id == task_id)
        result = await session.execute(query)
        task = result.first()
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        access_message = (f'GET task: '
                          f'task_id: {task_id}')
        send_email(sender_email, sender_password, receiver_email, subject, access_message)
        return task
    except Exception as e:
        error_message = str(e)
        send_email(sender_email, sender_password, receiver_email, subject, error_message)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)


@router.get("/", response_model=Page[Tasks])
async def get_all_tasks(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(tasks)
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


add_pagination(router)
