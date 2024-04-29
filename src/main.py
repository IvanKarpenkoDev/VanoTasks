import boto3
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserCreate
from src.projects.router import router as router_operation
from src.users.router import router as router_operation_users
from src.tasks.router import router as router_operation_tasks
from src.gigachat.routes import router as gigachat_router
from src.auth.schemas import UserRead

app = FastAPI(
    title="Vano Tasks"
)

Instrumentator().instrument(app).expose(app)

s3_client = boto3.client('s3', endpoint_url='http://localhost:4566',
                         aws_access_key_id='VANO@GMAIL.COMasdasdasd',
                         aws_secret_access_key='IAMVANOasdasdas'
                         )
s3_client.create_bucket(Bucket='vano')
s3_client.create_bucket(Bucket='file')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000", "http://172.21.176.1:9500/", "http://192.168.1.112:9500/"],
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
app.include_router(gigachat_router)
