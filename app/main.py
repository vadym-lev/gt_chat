import logging
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db import SessionLocal
from app.crud import create_task, get_task
from app.schemas import TextPayload
from app.message_queue import publish_message

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Database initialization on server startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # init_db()
    logger.info("Database initialized")
    yield


# FastAPI application
app = FastAPI(lifespan=lifespan)


# Dependency for the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoint to process text
@app.post("/process-text")
async def process_text(
        payload: TextPayload,
        db: Session = Depends(get_db)
):

    # Generate task_id
    task_id = str(uuid4())
    logger.info(f"Received task with ID: {task_id}")

    # Create a new task in the database
    task = create_task(db, task_id, payload.text, payload.type)

    # Asynchronously send the task to the message queue
    await publish_message(task_id, payload.text, payload.type)

    return {"task_id": task.task_id, "status": task.status}


# Endpoint to retrieve results
@app.get("/results/{task_id}")
async def get_results(
        task_id: str,
        db: Session = Depends(get_db)
):

    task = get_task(db, task_id)
    if not task:
        logger.warning(f"Task with ID {task_id} not found")
        raise HTTPException(status_code=404, detail="Task not found")

    logger.info(f"Returning results for task ID: {task_id}")

    return {
        "task_id": task.task_id,
        "original_text": task.original_text,
        "processed_text": task.processed_text,
        "word_count": task.word_count,
        "language": task.language,
        "status": task.status
    }

