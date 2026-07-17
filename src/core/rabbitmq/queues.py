from faststream.rabbit import RabbitQueue

from payments.constants import PAYMENTS_QUEUE, ROUTING_KEY_PAYMENT_CREATED, ROUTING_KEY_PAYMENT_FAILED, ROUTING_KEY_PAYMENT_RETRY
from core.rabbitmq.events import payment_exchange, payment_retry_exchange

payments_queue = RabbitQueue(
    name=PAYMENTS_QUEUE,
    routing_key=ROUTING_KEY_PAYMENT_CREATED,
    durable=True,
    arguments={
        "x-dead-letter-exchange": payment_retry_exchange.name,
        "x-dead-letter-routing-key": ROUTING_KEY_PAYMENT_RETRY,
    }
)

payment_retry_3s_queue = RabbitQueue(
    name=ROUTING_KEY_PAYMENT_RETRY,
    durable=True,
    routing_key=ROUTING_KEY_PAYMENT_RETRY,
    arguments={
        "x-message-ttl": 3000,
        "x-dead-letter-exchange": payment_exchange.name,
        "x-dead-letter-routing-key": ROUTING_KEY_PAYMENT_CREATED,
    },
)

payment_dead_queue = RabbitQueue(
    name=ROUTING_KEY_PAYMENT_FAILED,
    routing_key=ROUTING_KEY_PAYMENT_FAILED,
    durable=True,
)
