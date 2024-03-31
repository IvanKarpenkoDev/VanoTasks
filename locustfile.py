import random
import string

from locust import HttpUser, TaskSet, task, between


class MyTaskSet(TaskSet):

    @task
    def get_tasks(self):
        self.client.get("/tasks/")

    @task
    def get_projects(self):
        self.client.get("/projects/")

    @task
    def post_projects(self):
        payload = {
            "username": "vano@email.com",
            "password": "string"}
        self.client.post("/auth/login", data=payload)
        project_name = ''.join(random.choices(string.ascii_letters, k=10))
        self.client.post("/projects/", json={"project_name": project_name,
                                             "description": "asd",
                                             "project_code": "asd"})

    @task
    def post_tasks(self):
        payload = {
            "username": "vano@email.com",
            "password": "string"}
        self.client.post("/auth/login", data=payload)
        project_name = ''.join(random.choices(string.ascii_letters, k=10))
        self.client.post("/tasks/", json={
            "task_name": project_name,
            "description": "string",
            "assigned_to": 1,
            "project_id": 1
        })

    @task
    def get_projects(self):
        self.client.get("/users/")


class MyUser(HttpUser):
    tasks = [MyTaskSet]
    wait_time = between(1, 3)
