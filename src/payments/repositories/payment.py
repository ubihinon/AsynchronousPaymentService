import datetime
import decimal
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payments.dtos.payment import PaymentReadSchema
from payments.models.payment import Payment
from payments.repositories.base_payment import BasePaymentRepository


class PaymentRepository(BasePaymentRepository):
    async def create(
        self, price: decimal.Decimal, currency: str,  description: str, meta_data: dict, webhook_url: str
    ) -> PaymentReadSchema:
        payment_record = Payment(
            price=price,
            currency=currency,
            description=description,
            meta_data=meta_data,
            webhook_url=webhook_url,
        )
        self.session.add(payment_record)
        await self.session.commit()
        return PaymentReadSchema.model_validate(payment_record)

    async def update(self, payment_id: uuid.UUID) -> PaymentReadSchema | None:
        query = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(query)
        payment_record = result.scalar_one_or_none()

        if payment_record is None:
            return None

        payment_record.handled_at = datetime.datetime.now(datetime.UTC)
        await self.session.commit()
        await self.session.refresh(payment_record)

        return PaymentReadSchema.model_validate(payment_record)

    async def get_by_idempotency_key(self, idempotency_key: str) -> PaymentReadSchema | None:
        query = select(Payment).where(
            Payment.idempotency_key == idempotency_key
        )
        result = await self.session.execute(query)
        payment_record = result.scalar_one_or_none()

        return PaymentReadSchema.model_validate(payment_record) if payment_record else None
