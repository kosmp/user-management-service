import json
from datetime import datetime

import pika
from pika.adapters.blocking_connection import BlockingConnection


def send_message(email_to: str, reset_link: str, connection: BlockingConnection):
    channel = connection.channel()

    channel.queue_declare(queue="reset-password-stream", durable=True)

    properties = pika.BasicProperties(delivery_mode=2)
    properties.headers = {"subject": email_to}

    body = json.dumps(
        {"reset_link": reset_link, "publishing_datetime": datetime.now().isoformat()}
    )

    channel.basic_publish(
        exchange="",
        routing_key="reset-password-stream",
        body=body,
        properties=properties,
    )
