import pytest
from worker_app.worker import clean_text, word_count, process_task
from app.db import SessionLocal

def test_clean_text():
    text = "Hello, world! /// This is a test (with symbols)."
    cleaned = clean_text(text)
    assert cleaned == "Hello, world! This is a test (with symbols)."

def test_word_count():
    text = "Hello world! This is a test."
    count = word_count(text)
    assert count == 6

@pytest.mark.asyncio
async def test_process_task(mocker):

    mock_db = SessionLocal()
    mock_db.add = mocker.MagicMock()
    mock_db.commit = mocker.MagicMock()


    task_id = "test-task-id"
    text = "Hello, this is a test message."
    type_ = "chat_item"

    await process_task(task_id, text, type_)

    mock_db.commit.assert_called_once()