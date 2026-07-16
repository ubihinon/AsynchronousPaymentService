from faststream.rabbit import RabbitBroker

from core.settings import settings

broker = RabbitBroker(
    f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
)
