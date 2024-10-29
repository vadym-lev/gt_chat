import aio_pika
import pytest
from unittest.mock import AsyncMock, patch
from app.config import RABBITMQ_URL
from worker_app.worker import clean_text, word_count, process_task, connect_to_rabbitmq


def test_clean_text():
    """Test cleaning text with symbols and special characters."""
    text = "Hello, world!@#$%^"
    cleaned = clean_text(text)
    assert cleaned == "Hello, world!"


def test_word_count():
    """Test counting words in a cleaned text."""
    text = "Hello world! This is a test."
    count = word_count(text)
    assert count == 6


@pytest.mark.asyncio
@patch("worker_app.worker.SessionLocal")
@patch("worker_app.worker.update_task")
@patch("worker_app.worker.detect", return_value="en")
async def test_process_task(mock_detect, mock_update_task, mock_SessionLocal):
    """Test processing a task, including cleaning text, detecting language, counting words"""
    task_id = "test-task-id"
    text = "Hello,*&$ this is a test message."
    mock_db = mock_SessionLocal.return_value

    await process_task(task_id, text, mock_db)

    mock_detect.assert_called_once_with(text)
    mock_update_task.assert_called_once_with(
        mock_db, task_id, "Hello, this is a test message.", 6, "en"
    )
    mock_db.close.assert_called_once()


@pytest.mark.asyncio
@patch("worker_app.worker.aio_pika.connect_robust")
async def test_connect_to_rabbitmq_success(mock_connect_robust):
    """Test check successful connection to RabbitMQ"""
    mock_connect_robust.return_value = AsyncMock()

    connection = await connect_to_rabbitmq()

    mock_connect_robust.assert_called_once_with(RABBITMQ_URL)
    assert connection is not None


@pytest.mark.asyncio
@patch("worker_app.worker.aio_pika.connect_robust", side_effect=aio_pika.exceptions.AMQPConnectionError)
@patch("worker_app.worker.asyncio.sleep", return_value=None) # Skip sleep to speed up the test
async def test_connect_to_rabbitmq_failure(mock_sleep, mock_connect_robust):
    """Test for connect_to_rabbitmq with failed connection"""
    connection = await connect_to_rabbitmq()

    # Validation: should return None after 5 tries
    assert connection is None
    assert mock_connect_robust.call_count == 5
    assert mock_sleep.call_count == 5