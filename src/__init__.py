from fastapi.testclient import TestClient
import sys
import os

from src.main import app

client = TestClient(app)

def test_sum_endpoint():
    response = client.get("/tasks/")
    assert response.status_code == 200
