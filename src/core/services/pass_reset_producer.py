import json
from datetime import datetime

import pika
from pika.credentials import PlainCredentials
from pika.exchange_type import ExchangeType

from src.core import settings

credentials = PlainCredentials(
    settings.rabbitmq_default_user, settings.rabbitmq_default_pass
)

connection_parameters = pika.ConnectionParameters(
    "app-rabbitmq", settings.rabbitmq_port, "/", credentials
)


def send_message(email_to: str, reset_link: str):
    connection = pika.BlockingConnection(connection_parameters)

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

    connection.close()
