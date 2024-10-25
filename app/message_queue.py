import pika
import json
from .config import RABBITMQ_URL

# Publish task message to RabbitMQ
async def publish_message(task_id: str, text: str, type_: str):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # Message body to be sent to the queue
    message = {
        "task_id": task_id,
        "text": text,
        "type": type_
    }

    # Publish message to 'text_tasks' queue
    channel.basic_publish(exchange='', routing_key='text_tasks', body=json.dumps(message))
    connection.close()