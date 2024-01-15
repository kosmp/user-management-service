import json
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


def send_message(email_to: str, access_token: str):
    connection = pika.BlockingConnection(connection_parameters)

    channel = connection.channel()

    channel.exchange_declare(exchange="pubsub", exchange_type=ExchangeType.fanout)

    body = json.dumps({"email": email_to, "access_token": access_token})

    channel.basic_publish(exchange="pubsub", routing_key="letterbox", body=body)

    connection.close()
