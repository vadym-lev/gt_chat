import pika
import json
import re
from langdetect import detect
import asyncio
from .db import SessionLocal
from .crud import update_task

def clean_text(text):
    return re.sub(r"[^A-Za-z0-9\s,\.!\?\"\':\(\)-]", "", text)

def word_count(text):
    return len(text.split())


async def process_message(ch, method, properties, body):
    data = json.loads(body)
    task_id = data["task_id"]
    original_text = data["text"]

    cleaned_text = clean_text(original_text)
    language = detect(original_text)
    count = word_count(cleaned_text)

    db = SessionLocal()
    update_task(db, task_id, cleaned_text, count, language)
    db.close()


async def start_worker():
    connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@localhost:5672/"))
    channel = connection.channel()
    channel.queue_declare(queue='text_tasks')

    for method, properties, body in channel.consume(queue='text_tasks', auto_ack=True):
        await process_message(channel, method, properties, body)
        await asyncio.sleep(0)

    connection.close()


if __name__ == "__main__":
    asyncio.run(start_worker())