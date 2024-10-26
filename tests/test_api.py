from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_process_text():
    response = client.post(
        "/process-text",
        json={"text": "Hello world!", "type": "chat_item"}
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert response.json()["status"] == "processing"


def test_get_results_not_found():
    response = client.get("/results/nonexistent-task-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_process_text_validation_error():
    response = client.post(
        "/process-text",
        json={"text": "x" * 1000, "type": "chat_item"}  # сhat_item limit exceeded
    )
    assert response.status_code == 422
    assert "detail" in response.json()