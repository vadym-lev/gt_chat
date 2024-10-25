import asyncio
import aiohttp
import json
import logging
import aio_pika
import re
from langdetect import detect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text):
    return re.sub(r"[^\w\s:(),.!?“”'-]", "", text, flags=re.UNICODE)

def word_count(text):
    return len(text.split())

async def process_task(task_id, text, type_):
    cleaned_text = clean_text(text)
    language = detect(text)
    count = word_count(cleaned_text)

    async with aiohttp.ClientSession() as session:
        async with session.patch("http://fastapi_app:8000/tasks/", json={
            "task_id": task_id,
            "processed_text": cleaned_text,
            "word_count": count,
            "language": language
        }) as response:
            if response.ok:
                logger.info(f"Task {task_id} processed and stored.")
            else:
                logger.error(f"Failed to store task {task_id}: {response.status}")

async def connect_to_rabbitmq():
    for attempt in range(5):
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
            logger.info("Connected to RabbitMQ")
            return connection
        except aio_pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ is unavailable - retrying in 5 seconds...")
            await asyncio.sleep(5)
    logger.error("Could not connect to RabbitMQ after multiple attempts.")
    return None

async def consume():
    connection = await connect_to_rabbitmq()
    if connection is None:
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