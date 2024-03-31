from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserCreate
from src.projects.router import router as router_operation
from src.users.router import router as router_operation_users
from src.tasks.router import router as router_operation_tasks
from src.auth.schemas import UserRead



from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Vano Tasks"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000/", "http://172.21.176.1:9500/", "http://192.168.1.112:9500/"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_operation)
app.include_router(router_operation_users)
app.include_router(router_operation_tasks)
