from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_sum_endpoint():
    response = client.get("/tasks/")
    assert response.status_code == 200

