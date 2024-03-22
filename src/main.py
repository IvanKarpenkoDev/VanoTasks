from fastapi import FastAPI
from fastapi_users import router

from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserCreate
from src.operations.router import router as router_operation
from src.users.router import router as router_operation_users
from fastapi import Depends, Response
from src.auth.schemas import UserRead

app = FastAPI(
    title="Vano Tasks"
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


