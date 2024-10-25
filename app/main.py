import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .db import SessionLocal, init_db
from .crud import create_task, get_task
from .schemas import TextPayload
from .message_queue import publish_message

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI()

# Basic authentication setup
security = HTTPBasic()


# Database initialization on server startup
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized")


# Dependency for the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Verify credentials for basic authentication
def verify_credentials(credentials: HTTPBasicCredentials):
    correct_username = "admin"
    correct_password = "password"
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


# Endpoint to process text
@app.post("/process-text")
async def process_text(
        payload: TextPayload,
        db: Session = Depends(get_db),
        credentials: HTTPBasicCredentials = Depends(security)
):

    verify_credentials(credentials)

    # Validate text type
    if payload.type not in ["chat_item", "summary", "article"]:
        logger.error("Invalid text type")
        raise HTTPException(status_code=400, detail="Invalid text type")

    # Validate the `type` and length of `text`
    if payload.type == "chat_item" and len(payload.text) > 300:
        raise HTTPException(status_code=400, detail="Chat item text exceeds 300 characters.")
    elif payload.type == "summary" and len(payload.text) > 3000:
        raise HTTPException(status_code=400, detail="Summary text exceeds 3000 characters.")
    elif payload.type == "article" and len(payload.text) < 300000:
        raise HTTPException(status_code=400, detail="Article text is less than 300000 characters.")

    # Generate task_id
    task_id = str(uuid4())
    logger.info(f"Received task with ID: {task_id}")

    # Asynchronously send the task to the message queue
    await publish_message(task_id, payload.text, payload.type)

    return {"task_id": task_id, "status": "processing"}


# Endpoint to retrieve results
@app.get("/results/{task_id}")
async def get_results(
        task_id: str,
        db: Session = Depends(get_db),
        credentials: HTTPBasicCredentials = Depends(security)
):

    verify_credentials(credentials)

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