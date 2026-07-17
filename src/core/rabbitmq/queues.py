from faststream.rabbit import RabbitQueue

from payments.constants import PAYMENTS_QUEUE

payments_queue = RabbitQueue(
    name=PAYMENTS_QUEUE,
    routing_key="payment.created",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "payment.events.retry",
        "x-dead-letter-routing-key": "payment.events.retry.3s",
        # "x-dead-letter-exchange": "payment.events.dlx",
        # "x-dead-letter-routing-key": "payment.failed",
    }
)

payment_retry_10s_queue = RabbitQueue(
    name="payment.events.retry.3s",
    durable=True,
    routing_key="payment.events.retry.3s",
    arguments={
        # "x-message-ttl": 10000,
        "x-message-ttl": 3000,
        "x-dead-letter-exchange": "payment.events",
        "x-dead-letter-routing-key": "payment.created",
    },
)

payments_dead_queue = RabbitQueue(
    # name="payment.events.dead",
    name="payment.failed",
    routing_key="payment.failed",
    durable=True,
)
