import decimal

from payments.repositories.base_payment import BasePaymentRepository


class PaymentService:
    def __init__(self, repository: BasePaymentRepository):
        self.repository = repository

    async def create(
        self, price: decimal.Decimal, currency: str, description: str, meta_data: dict, webhook_url: str,
        idempotency_key: str
    ):
        payment = await self.repository.create(price, currency, description, meta_data, webhook_url, idempotency_key)
        return payment
