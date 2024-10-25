import pika
import json
import re
import time
from langdetect import detect
from sqlalchemy.orm import Session
from .db import SessionLocal, init_db
from .crud import update_task, create_task


init_db()

def clean_text(text):
    return re.sub(r"[^\w\s:(),.!?“”'-]", "", text, flags=re.UNICODE)


def word_count(text):
    return len(text.split())


def process_message(ch, method, properties, body):
    data = json.loads(body)
    task_id = data["task_id"]
    original_text = data["text"]

    cleaned_text = clean_text(original_text)
    language = detect(original_text)
    count = word_count(cleaned_text)

    db: Session = SessionLocal()
    create_task(db, task_id, original_text, data["type"])
    update_task(db, task_id, cleaned_text, count, language)
    db.close()


def start_worker():

    connection = None
    for _ in range(5):
        try:
            connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@rabbitmq:5672/"))
            break
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is unavailable - waiting before retrying...")
            time.sleep(5)

    if not connection:
        print("Failed to connect to RabbitMQ after multiple attempts.")
        return

    channel = connection.channel()
    channel.queue_declare(queue='text_tasks')
    channel.basic_consume(queue='text_tasks', on_message_callback=process_message, auto_ack=True)
    print("Worker is waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()