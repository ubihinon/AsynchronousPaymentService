import uuid

from sqlalchemy import select

from payments.constants import CurrencyEnum
from payments.dtos.payment import PaymentCreateDTO, PaymentMessageSchema
from payments.models.payment import Payment
from payments.repositories.base_payment import BasePaymentRepository


class PaymentRepository(BasePaymentRepository):
    async def create(self, dto: PaymentCreateDTO) -> Payment:
        payment_record = Payment(
            price=dto.price,
            currency=CurrencyEnum(dto.currency),
            description=dto.description,
            meta_data=dto.meta_data,
            webhook_url=dto.webhook_url,
            idempotency_key=dto.idempotency_key,
            request_payload_hash=dto.request_payload_hash,
        )
        self.session.add(payment_record)
        await self.session.flush()

        return payment_record

    async def update(self, payment_schema: PaymentMessageSchema) -> Payment | None:
        query = select(Payment).where(Payment.id == payment_schema.id)
        result = await self.session.execute(query)
        payment_record = result.scalar_one_or_none()

        if payment_record is None:
            return None

        payment_record.status = payment_schema.status
        payment_record.handled_at = payment_schema.handled_at

        await self.session.flush()
        await self.session.refresh(payment_record)

        return payment_record

    async def update_response_data(self, payment_id: uuid.UUID, response_data: dict) -> Payment | None:
        query = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(query)
        payment_record = result.scalar_one_or_none()

        if payment_record is None:
            return None

        payment_record.response_data = response_data
        await self.session.flush()
        await self.session.refresh(payment_record)

        return payment_record

    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        query = select(Payment).where(Payment.idempotency_key == idempotency_key)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get(self, payment_id: uuid.UUID) -> Payment | None:
        query = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
