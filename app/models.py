from sqlalchemy import Column, String, Integer
from .db import Base


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(String, primary_key=True, index=True)
    original_text = Column(String)
    processed_text = Column(String, nullable=True)
    type = Column(String)
    word_count = Column(Integer, nullable=True)
    language = Column(String, nullable=True)
    status = Column(String, default="processing")