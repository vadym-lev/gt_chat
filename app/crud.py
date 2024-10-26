from sqlalchemy.orm import Session
from app.models import Task


# Get task using task_id
def get_task(db: Session, task_id: str):
    return db.query(Task).filter(Task.task_id == task_id).first()


# Create a new task in the database (after processing)
def create_task(db: Session, task_id: str, original_text: str, type_: str):
    db_task = Task(task_id=task_id, original_text=original_text, type=type_, status="processing")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# Update task after processing (adding processed text, word count, and language)
def update_task(db: Session, task_id: str, processed_text: str, word_count: int, language: str):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if task:
        task.processed_text = processed_text
        task.word_count = word_count
        task.language = language
        task.status = "completed"
        db.commit()
        db.refresh(task)
    return task