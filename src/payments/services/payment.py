import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from payments.utils import hash_request_payload
from payments.dtos.payment import PaymentReadSchema
from payments.exceptions import IdempotencyKeyException
from payments.repositories.base_outbox import BaseOutboxRepository
from payments.repositories.base_payment import BasePaymentRepository
from payments.schemas.requests import PaymentCreateRequestSchema
from payments.schemas.responses import PaymentResponseSchema

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(
        self, session: AsyncSession, payment_repository: BasePaymentRepository, outbox_repository: BaseOutboxRepository
    ):
        self.session = session
        self.payment_repository = payment_repository
        self.outbox_repository = outbox_repository

    async def create(
        self, request_data: PaymentCreateRequestSchema, idempotency_key: str
    ) -> tuple[PaymentReadSchema, bool]:
        request_payload_hash = hash_request_payload(request_data)

        existing_payment = await self.get_by_idempotency_key(idempotency_key)
        if existing_payment:
            if existing_payment.request_payload_hash != request_payload_hash:
                raise IdempotencyKeyException()
            return existing_payment, False

        try:
            payment_orm = await self.payment_repository.create(
                request_data.price,
                request_data.currency,
                request_data.description,
                request_data.meta_data,
                request_data.webhook_url,
                idempotency_key,
                request_payload_hash
            )
            payment = PaymentReadSchema.model_validate(payment_orm)

            await self.outbox_repository.create(payment)

            response_data = PaymentResponseSchema.model_validate({
                "payment_id": payment.id,
                "status": payment.status,
                "created_at": payment.created_at
            })

            payment_updated_orm = await self.payment_repository.update_response_data(
                payment.id, response_data.model_dump(mode="json")
            )

            await self.session.commit()

            if payment_updated_orm:
                return PaymentReadSchema.model_validate(payment_updated_orm), True
            return payment, True
        except Exception as e:
            await self.session.rollback()
            logger.error(e)
            raise

    async def get(self, payment_id: uuid.UUID) -> PaymentReadSchema | None:
        payment_orm = await self.payment_repository.get(payment_id)
        return PaymentReadSchema.model_validate(payment_orm) if payment_orm else None

    async def get_by_idempotency_key(self, idempotency_key: str) -> PaymentReadSchema | None:
        payment_orm = await self.payment_repository.get_by_idempotency_key(idempotency_key)
        return PaymentReadSchema.model_validate(payment_orm) if payment_orm else None

    async def update(self, payment_schema: PaymentReadSchema) -> PaymentReadSchema | None:
        try:
            payment_orm = await self.payment_repository.update(payment_schema)

            await self.session.commit()

            return PaymentReadSchema.model_validate(payment_orm) if payment_orm else None
        except Exception as e:
            await self.session.rollback()
            logger.error(e)
            raise
