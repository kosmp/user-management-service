import json
from datetime import datetime
from src.logging_config import logger

import pika
from pika.credentials import PlainCredentials

from src.core import settings


class PikaClient:
    def __init__(
        self,
        rabbitmq_default_user: str,
        rabbitmq_default_pass: str,
        rabbitmq_host: str,
        rabbitmq_port: int,
        rabbitmq_vhost: str,
    ):
        credentials = PlainCredentials(rabbitmq_default_user, rabbitmq_default_pass)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                rabbitmq_host, rabbitmq_port, rabbitmq_vhost, credentials, heartbeat=0
            )
        )

        if self.connection:
            logger.info("Connection established successfully with RabbitMQ.")

    def send_message(self, email_to: str, reset_link: str, queue: str):
        channel = self.connection.channel()

        channel.queue_declare(queue=queue, durable=True)

        # delivery_mode=2 for guaranteed delivery instead of message throughput
        # Messages marked as persistent messages that are delivered to durable queues will be stored to the disk
        properties = pika.BasicProperties(delivery_mode=2)
        properties.headers = {"subject": email_to}

        body = json.dumps(
            {
                "reset_link": reset_link,
                "publishing_datetime": datetime.now().isoformat(),
            }
        )

        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=body,
            properties=properties,
        )

        logger.info("Message sent to RabbitMQ.")

    def __del__(self):
        self.connection.close()
        logger.info("Connection with RabbitMQ closed.")


pika_client_instance = PikaClient(
    rabbitmq_host=settings.rabbitmq_host,
    rabbitmq_port=settings.rabbitmq_port,
    rabbitmq_vhost=settings.rabbitmq_vhost,
    rabbitmq_default_user=settings.rabbitmq_default_user,
    rabbitmq_default_pass=settings.rabbitmq_default_pass,
)
