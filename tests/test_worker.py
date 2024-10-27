import pytest
from unittest.mock import MagicMock
from worker_app.worker import clean_text, word_count, process_task
from app.db import SessionLocal


def test_clean_text():
    """Test cleaning text with symbols and special characters."""
    text = "Hello, world!/// This is a test (with symbols)."
    cleaned = clean_text(text)
    assert cleaned == "Hello, world! This is a test (with symbols)."


def test_word_count():
    """Test counting words in a cleaned text."""
    text = "Hello world! This is a test."
    count = word_count(text)
    assert count == 6


@pytest.mark.asyncio
async def test_process_task(mocker):
    """Test processing a task, including cleaning text, detecting language, counting words, and updating the database."""

    # Set up a mock database session with required methods
    mock_db = MagicMock(spec=SessionLocal)
    mock_db.query = MagicMock()  # Mock the `query` method needed in `update_task`
    mock_db.commit = MagicMock()  # Mock the `commit` method needed in `update_task`
    mock_db.refresh = MagicMock()  # Mock the `refresh` method needed in `update_task`
    mock_db.close = MagicMock()  # Mock the `close` method needed at the end of `process_task`

    task_id = "test-task-id"
    text = "Hello, this is a test message."

    # Run the process_task function with the mock database
    await process_task(task_id, text, mock_db)

    # Ensure the database session is closed after processing
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    mock_db.close.assert_called_once()