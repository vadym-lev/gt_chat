import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal, init_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test_tasks.db"

engine = create_engine(DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    init_db()
    yield


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_process_text(client):
    response = client.post("/process-text", json={"text": "Hello world!", "type": "chat_item"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"


def test_get_results(client, test_db):
    response = client.get("/results/some-task-id")
    assert response.status_code == 404