from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from db import SessionLocal, init_db
from crud import create_task, get_task
from schemas import TextPayload
from message_queue import publish_message

app = FastAPI()


# DB initialization
@app.on_event("startup")
def startup_event():
    init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/process-text")
async def process_text(payload: TextPayload, db: Session = Depends(get_db)):
    task_id = str(uuid4())

    # Text type validation
    if payload.type not in ["chat_item", "summary", "article"]:
        raise HTTPException(status_code=400, detail="Invalid text type")

    # Create a new task in the database
    task = create_task(db, task_id, payload.text, payload.type)

    # Sending the task to the message queue
    publish_message(task_id, payload.text, payload.type)

    return {"task_id": task.task_id, "status": task.status}


@app.get("/results/{task_id}")
async def get_results(task_id: str, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.task_id,
        "original_text": task.original_text,
        "processed_text": task.processed_text,
        "word_count": task.word_count,
        "language": task.language,
        "status": task.status
    }