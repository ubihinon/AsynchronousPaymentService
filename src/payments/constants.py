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
PAYMENT_RETRY_ROUTING_KEYS = ["payment.retry.1", "payment.retry.2", "payment.retry.3"]
ROUTING_KEY_PAYMENT_FAILED = "payment.failed"
