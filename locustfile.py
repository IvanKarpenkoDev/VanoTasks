# import random
# import string
#
# from locust import HttpUser, TaskSet, task, between
#
#
# class MyTaskSet(TaskSet):
#
#     @task
#     def get_charts_tasks(self):
#         self.client.get("/tasks/charts/1")
#
#     @task
#     def put_projects(self):
#         payload = {
#             "username": "vano@email.com",
#             "password": "string"}
#         self.client.post("/auth/login", data=payload)
#         self.client.post("/tasks/task_comments/197", json={"comment_text": 'comments'})
#
#
# class MyUser(HttpUser):
#     tasks = [MyTaskSet]
#     wait_time = between(1, 3)
