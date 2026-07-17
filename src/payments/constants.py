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
PAYMENTS_EVENT = "payment.created"
