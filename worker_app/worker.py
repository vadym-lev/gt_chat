import re
from langdetect import detect
import asyncio
import aio_pika
import json
import logging
from app.db import SessionLocal
from app.crud import update_task
from app.config import RABBITMQ_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to clean the text by removing unwanted characters
def clean_text(text):
    return re.sub(r"[^\w\s:(),.!?“”'-]", "", text, flags=re.UNICODE)

# Function to count the words in the cleaned text
def word_count(text):
    return len(text.split())

async def process_task(task_id, text, type_):
    cleaned_text = clean_text(text)
    language = detect(text)
    count = word_count(cleaned_text)

    db = SessionLocal()
    try:
        update_task(db, task_id, cleaned_text, count, language)
    finally:
        db.close()

async def connect_to_rabbitmq():
    for attempt in range(5): # Retry up to 5 times
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            logger.info("Connected to RabbitMQ")
            return connection
        except aio_pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ is unavailable - retrying in 5 seconds...")
            await asyncio.sleep(5)
    logger.error("Could not connect to RabbitMQ after multiple attempts.")
    return None

async def consume():
    connection = await connect_to_rabbitmq()
    if connection is None: # Exit if the connection could not be established
        logger.error("Exiting due to RabbitMQ connection failure.")
        return

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("text_tasks")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body)
                    task_id = data["task_id"]
                    text = data["text"]
                    type_ = data["type"]

                    logger.info(f"Worker read task_id = {task_id}")
                    await process_task(task_id, text, type_)

if __name__ == "__main__":
    asyncio.run(consume())