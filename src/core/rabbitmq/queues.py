from faststream.rabbit import RabbitQueue

from payments.constants import PAYMENT_RETRY_ROUTING_KEYS, PAYMENTS_QUEUE, ROUTING_KEY_PAYMENT_CREATED, ROUTING_KEY_PAYMENT_FAILED
from core.rabbitmq.events import payment_exchange, payment_retry_exchange

payments_queue = RabbitQueue(
    name=PAYMENTS_QUEUE,
    routing_key=ROUTING_KEY_PAYMENT_CREATED,
    durable=True,
    arguments={
        "x-dead-letter-exchange": payment_retry_exchange.name,
        "x-dead-letter-routing-key": PAYMENT_RETRY_ROUTING_KEYS[0],
    }
)

payment_retry_queue_1 = RabbitQueue(
    name=PAYMENT_RETRY_ROUTING_KEYS[0],
    durable=True,
    routing_key=PAYMENT_RETRY_ROUTING_KEYS[0],
    arguments={
        "x-message-ttl": 3000,
        "x-dead-letter-exchange": payment_exchange.name,
        "x-dead-letter-routing-key": ROUTING_KEY_PAYMENT_CREATED,
    },
)

payment_retry_queue_2 = RabbitQueue(
    name=PAYMENT_RETRY_ROUTING_KEYS[1],
    durable=True,
    routing_key=PAYMENT_RETRY_ROUTING_KEYS[1],
    arguments={
        "x-message-ttl": 9000,
        "x-dead-letter-exchange": payment_exchange.name,
        "x-dead-letter-routing-key": ROUTING_KEY_PAYMENT_CREATED,
    },
)

payment_retry_queue_3 = RabbitQueue(
    name=PAYMENT_RETRY_ROUTING_KEYS[2],
    durable=True,
    routing_key=PAYMENT_RETRY_ROUTING_KEYS[2],
    arguments={
        "x-message-ttl": 27000,
        "x-dead-letter-exchange": payment_exchange.name,
        "x-dead-letter-routing-key": ROUTING_KEY_PAYMENT_CREATED,
    },
)

payment_dead_queue = RabbitQueue(
    name=ROUTING_KEY_PAYMENT_FAILED,
    routing_key=ROUTING_KEY_PAYMENT_FAILED,
    durable=True,
)
