import enum


class CurrencyEnum(str, enum.Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

PAYMENTS_QUEUE = "payments.new"
ROUTING_KEY_PAYMENT_CREATED = "payment.created"
ROUTING_KEY_PAYMENT_RETRY = "payment.retry"
ROUTING_KEY_PAYMENT_FAILED = "payment.failed"
