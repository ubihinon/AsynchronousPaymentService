from faststream.rabbit import ExchangeType, RabbitExchange

from payments.constants import ROUTING_KEY_PAYMENT_FAILED

payment_exchange = RabbitExchange(
    name="payment.events",
    type=ExchangeType.TOPIC,
    durable=True,
)

payment_retry_exchange = RabbitExchange(
    name="payment.events.retry",
    type=ExchangeType.DIRECT,
    durable=True,
)

payment_dlx = RabbitExchange(
    name=ROUTING_KEY_PAYMENT_FAILED,
    type=ExchangeType.DIRECT,
    durable=True,
)
