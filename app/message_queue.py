import pika
import json
from config import RABBITMQ_URL

def publish_message(task_id, text, type_):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    message = {
        "task_id": task_id,
        "text": text,
        "type": type_
    }

    channel.basic_publish(
        exchange='',
        routing_key='text_tasks',
        body=json.dumps(message)
    )
    connection.close()