import json
from datetime import datetime

from pydantic import UUID4

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

        self.channel = self.connection.channel()

        self.channel.basic_qos(prefetch_count=3)

        self.channel.exchange_declare("email-x", exchange_type="direct")
        self.channel.exchange_declare("email-dlx", exchange_type="direct")

        self.channel.queue_declare(
            queue=settings.rabbitmq_email_queue_name,
            durable=True,
            arguments={
                "x-queue-type": "quorum",
                "x-dead-letter-exchange": "email-dlx",
            },
        )

        self.channel.queue_bind(
            exchange="email-x", queue=settings.rabbitmq_email_queue_name
        )

    def send_message(self, email_to: str, user_id: str, reset_link: str):
        # delivery_mode=2 for guaranteed delivery instead of message throughput
        # Messages marked as persistent messages that are delivered to durable queues will be stored to the disk
        properties = pika.BasicProperties(delivery_mode=2)
        properties.headers = {"subject": email_to}

        body = json.dumps(
            {
                "user_id": user_id,
                "reset_link": reset_link,
                "publishing_datetime": datetime.now().isoformat(),
            }
        )

        self.channel.basic_publish(
            exchange="email-x",
            routing_key=settings.rabbitmq_email_queue_name,
            body=body,
            properties=properties,
        )

        logger.info("Message sent to RabbitMQ.")

    def __del__(self):
        self.connection.close()


pika_client_instance = PikaClient(
    rabbitmq_host=settings.rabbitmq_host,
    rabbitmq_port=settings.rabbitmq_port,
    rabbitmq_vhost=settings.rabbitmq_vhost,
    rabbitmq_default_user=settings.rabbitmq_default_user,
    rabbitmq_default_pass=settings.rabbitmq_default_pass,
)
