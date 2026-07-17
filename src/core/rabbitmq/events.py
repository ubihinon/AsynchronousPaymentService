from faststream.rabbit import ExchangeType, RabbitExchange

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
    name="payment.events.dlx",
    type=ExchangeType.DIRECT,
    durable=True,
)
