import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from src.main import app
from src.tasks.models import tasks
from src.tasks.schemas import TasksRequest

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


@pytest.fixture(scope="session")
def db():
    yield async_session


@pytest.fixture(scope="function")
async def session(db):
    async with db() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    tasks.metadata.create_all(engine)
    yield
    clear_mappers()
    tasks.metadata.drop_all(engine)


def test_create_task():
    client = TestClient(app)

    # Неверный запрос
    response = client.post("/tasks/", json={})
    assert response.status_code == 422  # Ошибка валидации

    # Верный запрос
    task_data = {
        "task_name": "Test Task",
        "description": "Test Description",
        "assigned_to": 1,
        "project_id": 1
    }
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 204  # Успешное создание задачи


def test_get_task_by_id(session):
    client = TestClient(app)

    # Создаем тестовую задачу
    task_data = {
        "task_name": "Test Task",
        "description": "Test Description",
        "assigned_to": 1,
        "project_id": 1
    }
    session.execute(tasks.insert().values(**task_data))
    session.commit()

    # Получаем созданную задачу по ID
    response = client.get("/tasks/1")
    assert response.status_code == 200  # Успешное получение задачи
    assert response.json()["task_name"] == "Test Task"


def test_get_users_tasks_by_user_id(session):
    client = TestClient(app)

    # Создаем тестовые задачи для пользователя
    task_data = {
        "task_name": "Test Task",
        "description": "Test Description",
        "assigned_to": 1,
        "project_id": 1,
        "created_by": 1
    }
    session.execute(tasks.insert().values(**task_data))
    session.commit()

    # Получаем задачи пользователя по его ID
    response = client.get("/tasks/user_tasks/1")
    assert response.status_code == 200  # Успешное получение задач пользователя


def test_get_tasks_by_project_id(session):
    client = TestClient(app)

    # Создаем тестовые задачи для проекта
    task_data = {
        "task_name": "Test Task",
        "description": "Test Description",
        "assigned_to": 1,
        "project_id": 1,
        "created_by": 1
    }
    session.execute(tasks.insert().values(**task_data))
    session.commit()

    # Получаем задачи для проекта по его ID
    response = client.get("/tasks/project_tasks/1")
    assert response.status_code == 200  # Успешное получение задач для проекта
