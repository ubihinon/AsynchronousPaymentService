import decimal
import uuid

from payments.repositories.base_payment import BasePaymentRepository


class PaymentService:
    def __init__(self, repository: BasePaymentRepository):
        self.repository = repository

    async def create(
        self, price: decimal.Decimal, currency: str, description: str, meta_data: dict, webhook_url: str,
        idempotency_key: str, request_payload_hash: str
    ):
        payment = await self.repository.create(
            price, currency, description, meta_data, webhook_url, idempotency_key, request_payload_hash
        )
        return payment

    async def update_response_data(self, payment_id: uuid.UUID, response_data: dict):
        return await self.repository.update_response_data(payment_id, response_data)

    async def get(self, payment_id: uuid.UUID):
        payment = await self.repository.get(payment_id)
        return payment

    async def get_by_idempotency_key(self, idempotency_key: str):
        payment = await self.repository.get_by_idempotency_key(idempotency_key)
        return payment
